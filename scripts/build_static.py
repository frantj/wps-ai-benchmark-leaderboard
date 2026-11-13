#!/usr/bin/env python3
"""Write the crawlable, no-JavaScript copies of the site's data-driven content.

The pages render client-side, so the leaderboard rows, criteria and agent
results are not in the HTML a non-rendering crawler (most AI crawlers) reads.
This script writes them into marker-delimited blocks in the pages, plus the
JSON-LD, sitemap.xml, the standings section of llms.txt, and leaderboard.md.

    python3 scripts/build_static.py           # regenerate, in place
    python3 scripts/build_static.py --check   # exit 1 if anything is stale

Run it after changing data/*.json, data/faq.json, or any page. Generated
output is committed: what is in the tree is what is served. Standard library
only; no network.

Blocks look like  <!-- STATIC:name:START --> ... <!-- STATIC:name:END -->.
Do not edit between the markers by hand.
"""
import datetime
import hashlib
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://wpsleaderboard.ai"
ORG_ID = SITE + "/#organization"
WEBSITE_ID = SITE + "/#website"
STATE_FILE = ROOT / "scripts" / "page-state.json"
PASS_MARK = 0.60

# file, URL path, breadcrumb name, schema.org page type
PAGES = [
    ("index.html", "/", "Leaderboard", "WebPage"),
    ("benchmark.html", "/benchmark", "The Benchmark", "WebPage"),
    ("methodology.html", "/methodology", "Methodology", "WebPage"),
    ("our-agent.html", "/our-agent", "Our Agent", "WebPage"),
    ("media.html", "/media", "Media", "CollectionPage"),
    ("about.html", "/about", "About", "AboutPage"),
    ("contact.html", "/contact", "Contact", "ContactPage"),
]

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
TIER_ORDER = ["T1", "T1-neutral", "T2", "T3"]  # same order as the page scripts


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- helpers

def esc(value):
    text = html.escape(str(value), quote=True)
    if "{{" in text:
        # The blocks sit inside the page template; a literal {{ would be
        # read as a binding.
        raise BuildError("data contains '{{': %r" % value)
    return text


def fmt(value):
    """Two decimals, matching the pages' toFixed(2)."""
    return "—" if value is None else format(value, ".2f")


def long_date(iso):
    y, m, d = (int(p) for p in iso.split("-"))
    return "%d %s %d" % (d, MONTHS[m - 1], y)


def block_re(name):
    return re.compile(
        r"(<!-- STATIC:%s:START -->)(.*?)(<!-- STATIC:%s:END -->)" % (re.escape(name), re.escape(name)),
        re.S,
    )


def set_block(text, name, body, where):
    pattern = block_re(name)
    if len(pattern.findall(text)) != 1:
        raise BuildError("%s: expected exactly one STATIC:%s block" % (where, name))
    return pattern.sub(lambda m: m.group(1) + "\n" + body.strip("\n") + "\n" + m.group(3), text)


def hidden(body):
    """Wrap in a constant-false conditional: present in the raw HTML for
    crawlers and no-JS readers, never rendered by the page runtime (which
    renders the live, interactive version instead)."""
    return '<sc-if value="{{ false }}">\n' + body.strip("\n") + "\n</sc-if>"


def table(headers, rows, caption):
    out = ["<table>", "<caption>%s</caption>" % esc(caption), "<thead><tr>"]
    out += ['<th scope="col">%s</th>' % esc(h) for h in headers]
    out.append("</tr></thead>")
    out.append("<tbody>")
    for row in rows:
        out.append("<tr>" + "".join("<td>%s</td>" % esc(c) for c in row) + "</tr>")
    out += ["</tbody>", "</table>"]
    return "\n".join(out)


def jsonld(graph):
    doc = {"@context": "https://schema.org", "@graph": graph}
    body = json.dumps(doc, indent=2, ensure_ascii=False).replace("</", "<\\/")
    return '<script type="application/ld+json">\n%s\n</script>' % body


def head_field(text, pattern, where, what):
    m = re.search(pattern, text, re.S)
    if not m:
        raise BuildError("%s: could not find %s" % (where, what))
    return html.unescape(m.group(1)).strip()


# ---------------------------------------------------------------- data

def load():
    rows = json.loads((ROOT / "data" / "leaderboard.json").read_text(encoding="utf-8"))
    crit = json.loads((ROOT / "data" / "criteria.json").read_text(encoding="utf-8"))
    faq = json.loads((ROOT / "data" / "faq.json").read_text(encoding="utf-8"))
    return rows, crit["criteria"], crit["tiers"], faq


def ranked(rows):
    return sorted(rows, key=lambda r: -r["overall"])


def general_models(rows):
    """Same filter and order as index.html: not ours, by overall descending."""
    return ranked([r for r in rows if not r.get("isOurs")])


def gap_finding(models):
    """The headline finding in plain words: how many models score lower on
    gender-sensitivity when the prompt does not mention gender (T3) than when
    it spells the gender dimensions out (T1). Counted, never assumed."""
    rows = [r for r in models if "T1" in (r.get("genderByTier") or {}) and "T3" in r["genderByTier"]]
    if not rows:
        raise BuildError("no model has both T1 and T3 gender scores")
    cued = [r["genderByTier"]["T1"]["score"] for r in rows]
    sparse = [r["genderByTier"]["T3"]["score"] for r in rows]
    with_gap = sum(1 for c, s in zip(cued, sparse) if s < c)
    who = ("All %d" % len(rows)) if with_gap == len(rows) else ("%d of the %d" % (with_gap, len(rows)))
    top = rows[0]  # models arrive ranked by overall score
    return (
        "%s general-purpose AI models tested show the WPS Competence Gap. When a prompt spells out the gender "
        "dimensions, they score between %s and %s out of 1.00 on gender-sensitivity. On short, realistic requests "
        "that do not mention gender, they score between %s and %s. The top-ranked model, %s, falls from %s to %s."
        % (who, fmt(min(cued)), fmt(max(cued)), fmt(min(sparse)), fmt(max(sparse)), top["label"],
           fmt(top["genderByTier"]["T1"]["score"]), fmt(top["genderByTier"]["T3"]["score"]))
    )


def score_table(systems, criteria, caption, with_rank):
    headers = (["Rank"] if with_rank else []) + ["System", "Provider", "Evaluated", "Overall"]
    headers += [c["name"] for c in criteria]
    body = []
    for i, r in enumerate(systems, 1):
        row = ([i] if with_rank else []) + [r["label"], r["provider"], long_date(r["date"]), fmt(r["overall"])]
        row += [fmt(r["criteria"].get(c["id"])) for c in criteria]
        body.append(row)
    return table(headers, body, caption)


def tier_table(systems, tiers, caption):
    meta = {t["id"]: t for t in tiers}
    headers = ["System"] + ["%s — %s" % (t, meta[t]["name"]) for t in TIER_ORDER]
    body = []
    for r in systems:
        cells = [r["label"]]
        for t in TIER_ORDER:
            cell = (r.get("genderByTier") or {}).get(t)
            if not cell:
                cells.append("—")
                continue
            text = fmt(cell["score"])
            if cell["n"] < meta[t]["count"]:
                text += " (n=%d/%d)" % (cell["n"], meta[t]["count"])
            cells.append(text)
        body.append(cells)
    return table(headers, body, caption)


def notes_list(systems):
    items = []
    for r in systems:
        parts = [p for p in (r.get("description"), r.get("note")) if p]
        if parts:
            items.append("<li><strong>%s</strong> (%s, overall %s): %s</li>"
                         % (esc(r["label"]), esc(r["provider"]), fmt(r["overall"]), esc(" ".join(parts))))
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


# ---------------------------------------------------------------- page blocks

def index_blocks(rows, criteria, tiers):
    models = general_models(rows)
    top = models[0]
    newest = max(r["date"] for r in models)
    passing = sum(1 for r in models if r["overall"] >= PASS_MARK)  # raw value, not the rounded display
    summary = (
        '<p style="font-size:14.5px;line-height:1.6;color:var(--osf-navy);margin:12px 0 0;max-width:760px;">'
        '<strong>Latest results (<time datetime="%s">%s</time>):</strong> '
        "%s Overall, %s (%s) ranks first at %s, and %d of the %d models clear the %s pass threshold.</p>"
        % (newest, long_date(newest), esc(gap_finding(models)), esc(top["label"]), esc(top["provider"]),
           fmt(top["overall"]), passing, len(models), fmt(PASS_MARK))
    )
    static = "\n".join([
        "<div>",
        "<p>Static copy of the leaderboard for readers without JavaScript. Scores run from 0.00 to 1.00; "
        "%s is the pass threshold. Results last updated %s.</p>" % (fmt(PASS_MARK), long_date(newest)),
        score_table(models, criteria,
                    "WPS AI Leaderboard: overall and per-criterion scores, general-purpose models, benchmark v6", True),
        tier_table(models, tiers,
                   "Gender-sensitivity / WPS integration score by prompt tier (the fall from T1 to T3 is the WPS Competence Gap)"),
        "<p>Notes on each system:</p>",
        notes_list(models),
        "</div>",
    ])
    return {"summary": summary, "leaderboard": hidden(static)}


def agent_blocks(text, rows, criteria, tiers):
    m = re.search(r"SUPPORTED_IDS\s*=\s*\[(.*?)\];", text, re.S)  # ids contain ']'
    ids = re.findall(r"'([^']+)'", m.group(1)) if m else []
    builds = ranked([r for r in rows if r["id"] in ids])
    if not ids or len(builds) != len(ids):
        raise BuildError("our-agent.html: SUPPORTED_IDS not found or not all in leaderboard.json")
    stages = re.findall(r"\{ num: '([^']*)', title: '([^']*)', desc: '([^']*)' \}", text)
    if not stages:
        raise BuildError("our-agent.html: could not read the stages list from the page script")
    stage_html = "<ol>\n" + "\n".join(
        "<li><strong>%s.</strong> %s</li>" % (esc(t), esc(d)) for _, t, d in stages) + "\n</ol>"
    results = "\n".join([
        "<div>",
        "<p>Static copy of the agent's benchmark results for readers without JavaScript.</p>",
        score_table(builds, criteria, "WPS Agent builds available now: overall and per-criterion scores, benchmark v6", False),
        tier_table(builds, tiers, "WPS Agent: gender-sensitivity / WPS integration score by prompt tier"),
        notes_list(builds),
        "</div>",
    ])
    return {"agent-stages": hidden(stage_html), "agent-results": hidden(results)}


def benchmark_blocks(text, rows, criteria, tiers, faq):
    def crit_list(group):
        return "<ul>\n" + "\n".join(
            "<li><strong>%s.</strong> %s</li>" % (esc(c["name"]), esc(c["question"]))
            for c in criteria if c["group"] == group) + "\n</ul>"

    tier_html = "<ul>\n" + "\n".join(
        "<li><strong>%s — %s</strong> (%d scenarios). %s</li>"
        % (esc(t["id"]), esc(t["name"]), t["count"], esc(t.get("description", ""))) for t in tiers) + "\n</ul>"

    chart = re.findall(r"\{ id: '([^']+)', group: '([^']+)' \}", text)
    if not chart:
        raise BuildError("benchmark.html: could not read TIER_CHART_MODELS from the page script")
    by_id = {r["id"]: r for r in rows}
    chart_rows = [by_id[i] for i, _ in chart if i in by_id]
    chart_html = tier_table(chart_rows, tiers, "Gender-sensitivity / WPS integration score by prompt tier, selected models")

    qa = ['<h2 style="font-family:var(--font-serif);font-size:24px;color:var(--osf-navy);margin:36px 0 14px;">Common questions</h2>']
    for item in faq:
        qa.append('<h3 style="font-family:var(--font-serif);font-size:18px;color:var(--osf-navy);margin:22px 0 6px;">%s</h3>' % esc(item["q"]))
        qa.append('<p style="font-size:16px;line-height:1.75;color:var(--text-secondary);margin:0;">%s</p>' % esc(item["a"]))
    return {
        "criteria-standard": hidden(crit_list("standard")),
        "criteria-adversarial": hidden(crit_list("adversarial")),
        "tiers": hidden(tier_html),
        "tier-chart": hidden(chart_html),
        "faq": "\n".join(qa),
    }


def media_items(text):
    items = re.findall(
        r'<article>\s*<a href="([^"]+)".*?text-transform:uppercase[^>]*>([^<]+)</div>\s*'
        r'<time datetime="([^"]+)".*?<h2[^>]*>([^<]+)</h2>', text, re.S)
    if not items:
        raise BuildError("media.html: no <article> items found")
    return [(html.unescape(u), html.unescape(p).strip(), d, html.unescape(t).strip()) for u, p, d, t in items]


# ---------------------------------------------------------------- JSON-LD

def page_graph(fname, path, crumb, ptype, text, modified, rows, criteria, faq):
    url = SITE + path
    title = head_field(text, r"<title>(.*?)</title>", fname, "<title>")
    desc = head_field(text, r'<meta name="description" content="([^"]*)"', fname, "meta description")
    graph = [{
        "@type": ptype, "@id": url + "#webpage", "url": url, "name": title, "description": desc,
        "isPartOf": {"@id": WEBSITE_ID}, "publisher": {"@id": ORG_ID},
        "inLanguage": "en", "dateModified": modified,
    }]
    if path != "/":
        graph.append({
            "@type": "BreadcrumbList", "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Leaderboard", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": crumb, "item": url},
            ],
        })
    if fname == "index.html":
        models = general_models(rows)
        newest = max(r["date"] for r in models)
        graph.append({
            "@type": "Dataset", "@id": SITE + "/#results",
            "name": "WPS AI Leaderboard results (benchmark v6)",
            "description": "Overall and per-criterion scores for %d general-purpose AI models on the Women, Peace and "
                           "Security (WPS) AI Benchmark v6: 30 scenarios scored against an 11-criterion rubric by three "
                           "independent AI judges. Scores run from 0.00 to 1.00 with a %s pass threshold."
                           % (len(models), fmt(PASS_MARK)),
            "url": SITE + "/", "dateModified": newest, "inLanguage": "en",
            "creator": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID},
            "isBasedOn": SITE + "/benchmark",
            "variableMeasured": ["Overall score"] + [c["name"] for c in criteria],
            "distribution": [
                {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + "/data/leaderboard.json"},
                {"@type": "DataDownload", "encodingFormat": "text/markdown", "contentUrl": SITE + "/leaderboard.md"},
            ],
        })
        graph.append({
            "@type": "ItemList", "@id": SITE + "/#ranking",
            "name": "WPS AI Leaderboard ranking of general-purpose AI models",
            "itemListOrder": "https://schema.org/ItemListOrderDescending",
            "numberOfItems": len(models),
            "itemListElement": [{
                "@type": "ListItem", "position": i, "name": "%s (%s)" % (r["label"], r["provider"]),
                "description": "Overall score %s of 1.00, evaluated %s." % (fmt(r["overall"]), long_date(r["date"])),
            } for i, r in enumerate(models, 1)],
        })
    elif fname == "our-agent.html":
        graph.append({
            "@type": "SoftwareApplication", "@id": url + "#agent", "name": "WPS AI Agent",
            "applicationCategory": "Research and analysis assistant", "operatingSystem": "Web",
            "description": desc, "url": url, "creator": {"@id": ORG_ID},
        })
    elif fname == "benchmark.html":
        graph.append({
            "@type": "FAQPage", "@id": url + "#faq",
            "mainEntity": [{"@type": "Question", "name": i["q"],
                            "acceptedAnswer": {"@type": "Answer", "text": i["a"]}} for i in faq],
        })
    elif fname == "media.html":
        graph.append({
            "@type": "ItemList", "@id": url + "#items",
            "itemListElement": [{
                "@type": "ListItem", "position": n,
                "item": {"@type": "Article", "headline": t, "url": u, "datePublished": d,
                         "publisher": {"@type": "Organization", "name": p.split(" · ")[0]}},
            } for n, (u, p, d, t) in enumerate(media_items(text), 1)],
        })
    return graph


# ---------------------------------------------------------------- other files

def leaderboard_md(rows, criteria, tiers):
    models = general_models(rows)
    newest = max(r["date"] for r in models)
    meta = {t["id"]: t for t in tiers}

    def md_table(headers, body):
        lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
        lines += ["| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |" for row in body]
        return "\n".join(lines)

    out = [
        "# WPS AI Leaderboard — results",
        "",
        "> Markdown copy of %s/ for AI agents and researchers. Generated from data/leaderboard.json; do not edit by hand." % SITE,
        "",
        "How general-purpose AI models score on the Women, Peace and Security (WPS) AI Benchmark v6: 30 realistic "
        "peace-and-security scenarios, an 11-criterion rubric, three independent AI judges. Scores run from 0.00 to 1.00; "
        "%s is the pass threshold. Published by Our Secure Future, a PAX sapiens program." % fmt(PASS_MARK),
        "",
        "Results last updated: %s." % long_date(newest),
        "",
        "## Main finding",
        "",
        gap_finding(models),
        "",
        "## Overall ranking",
        "",
        md_table(["Rank", "System", "Provider", "Evaluated", "Overall"],
                 [[i, r["label"], r["provider"], long_date(r["date"]), fmt(r["overall"])] for i, r in enumerate(models, 1)]),
        "",
        "## Scores by criterion",
        "",
        md_table(["System"] + [c["name"] for c in criteria],
                 [[r["label"]] + [fmt(r["criteria"].get(c["id"])) for c in criteria] for r in models]),
        "",
        "## Gender-sensitivity / WPS integration by prompt tier",
        "",
        "The fall from cued (T1) to sparse (T3) prompts is the WPS Competence Gap.",
        "",
    ]
    tier_rows = []
    for r in models:
        cells = [r["label"]]
        for t in TIER_ORDER:
            cell = (r.get("genderByTier") or {}).get(t)
            cells.append("—" if not cell else fmt(cell["score"]) + (
                " (n=%d/%d)" % (cell["n"], meta[t]["count"]) if cell["n"] < meta[t]["count"] else ""))
        tier_rows.append(cells)
    out += [
        md_table(["System"] + ["%s %s" % (t, meta[t]["name"]) for t in TIER_ORDER], tier_rows),
        "",
        "## Notes on each system",
        "",
    ]
    out += ["- **%s** (%s): %s" % (r["label"], r["provider"], r["note"]) for r in models if r.get("note")]
    out += [
        "",
        "## How to read these scores",
        "",
        "- Scores are model-graded by three AI judges, not human-graded.",
        "- Differences under roughly 0.10–0.15 are directional, not a reliable ranking.",
        "- This is not a safety certification and must not be used as clearance for operational, warfare or targeting decisions.",
        "- Our Secure Future's own WPS Agent is scored on the same benchmark; its results are at %s/our-agent." % SITE,
        "- Methodology: %s/methodology. Benchmark and rubric: %s/benchmark." % (SITE, SITE),
        "",
    ]
    return "\n".join(out)


def llms_standings(rows):
    models = general_models(rows)
    newest = max(r["date"] for r in models)
    passing = sum(1 for r in models if r["overall"] >= PASS_MARK)
    lines = [
        "## Current standings",
        "",
        gap_finding(models),
        "",
        "General-purpose models, overall score (0.00–1.00, pass threshold %s), results last updated %s. "
        "%d of %d clear the threshold. Full table: [leaderboard.md](%s/leaderboard.md)."
        % (fmt(PASS_MARK), long_date(newest), passing, len(models), SITE),
        "",
    ]
    lines += ["%d. %s (%s) — %s" % (i, r["label"], r["provider"], fmt(r["overall"])) for i, r in enumerate(models, 1)]
    return "\n".join(lines) + "\n"


def set_llms_section(text, section):
    pattern = re.compile(r"## Current standings\n.*?(?=\n## )", re.S)
    if len(pattern.findall(text)) != 1:
        raise BuildError("llms.txt: expected exactly one '## Current standings' section followed by another section")
    return pattern.sub(lambda m: section, text)


def sitemap(modified):
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for fname, path, _, _ in PAGES:
        out += ["  <url>", "    <loc>%s%s</loc>" % (SITE, path), "    <lastmod>%s</lastmod>" % modified[fname], "  </url>"]
    out.append("</urlset>")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- build

def content_hash(text):
    """Hash of a page ignoring its JSON-LD block, which carries the date."""
    stripped = block_re("jsonld").sub("", text)
    return hashlib.sha256(stripped.encode("utf-8")).hexdigest()[:16]


def build(check):
    rows, criteria, tiers, faq = load()
    state = json.loads(STATE_FILE.read_text(encoding="utf-8")) if STATE_FILE.exists() else {}
    today = datetime.date.today().isoformat()
    outputs, new_state, stale_dates = {}, {}, []

    for fname, path, crumb, ptype in PAGES:
        text = (ROOT / fname).read_text(encoding="utf-8")
        if fname == "index.html":
            blocks = index_blocks(rows, criteria, tiers)
        elif fname == "our-agent.html":
            blocks = agent_blocks(text, rows, criteria, tiers)
        elif fname == "benchmark.html":
            blocks = benchmark_blocks(text, rows, criteria, tiers, faq)
        else:
            blocks = {}
        for name, body in blocks.items():
            text = set_block(text, name, body, fname)

        digest = content_hash(text)
        prev = state.get(fname, {})
        if prev.get("hash") == digest:
            modified = prev["modified"]
        else:
            modified = today
            stale_dates.append(fname)
        new_state[fname] = {"hash": digest, "modified": modified}
        graph = page_graph(fname, path, crumb, ptype, text, modified, rows, criteria, faq)
        outputs[fname] = set_block(text, "jsonld", jsonld(graph), fname)

    modified = {f: new_state[f]["modified"] for f in new_state}
    outputs["sitemap.xml"] = sitemap(modified)
    outputs["leaderboard.md"] = leaderboard_md(rows, criteria, tiers)
    outputs["llms.txt"] = set_llms_section((ROOT / "llms.txt").read_text(encoding="utf-8"), llms_standings(rows))
    outputs["scripts/page-state.json"] = json.dumps(new_state, indent=2, sort_keys=True) + "\n"

    changed = []
    for rel, body in outputs.items():
        target = ROOT / rel
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current != body:
            changed.append(rel)
            if not check:
                target.write_text(body, encoding="utf-8")

    if check:
        if changed:
            print("STALE — run `python3 scripts/build_static.py` and commit the result:")
            for rel in changed:
                print("  " + rel)
            return 1
        print("Static copies are up to date (%d files checked)." % len(outputs))
        return 0
    print("Wrote: " + (", ".join(changed) if changed else "nothing (already up to date)"))
    if stale_dates:
        print("Last-modified date set to %s for: %s" % (today, ", ".join(stale_dates)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(build("--check" in sys.argv[1:]))
    except BuildError as err:
        print("build_static: " + str(err), file=sys.stderr)
        sys.exit(2)
