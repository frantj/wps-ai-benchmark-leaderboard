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
DIRECTIONAL_BAND = 0.10  # RELIABILITY.md: smaller differences are directional only

# The benchmark has no validated pass mark (benchmark/v6/README.md, section 5).
# Results must not be labelled pass/fail. `lint` enforces this on everything
# the site serves; ALLOWED are the places that say so.
BANNED = re.compile(r"pass mark|pass threshold|passing threshold|meets threshold|fails threshold|"
                    r"below threshold|clears? the|clears all", re.I)
ALLOWED = re.compile(r"no pass mark|a pass mark\?|not pass marks|no validated pass mark", re.I)
LINTED = ["index.html", "benchmark.html", "methodology.html", "our-agent.html", "media.html", "about.html",
          "contact.html", "404.html", "llms.txt", "leaderboard.md", "data/faq.json", "data/leaderboard.json"]

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
    TIER_COUNTS.update({t["id"]: t["count"] for t in crit["tiers"]})
    return rows, crit["criteria"], crit["tiers"], faq


def ranked(rows):
    return sorted(rows, key=lambda r: -r["overall"])


def general_models(rows):
    """Same filter and order as index.html: not ours, by overall descending."""
    return ranked([r for r in rows if not r.get("isOurs")])


def gap_finding(models):
    """The headline finding in plain words: how many models score lower on
    gender-sensitivity on sparse prompts with no gender cue (T3) than on
    detailed prompts that spell the gender dimensions out (T1). T3 differs
    from T1 in more than the cue (terse, incomplete, fictional settings), so
    the text never says the cue alone causes the fall. Counted, never
    assumed, and stated as a comparison because the benchmark has no pass
    mark."""
    rows = [r for r in models if "T1" in (r.get("genderByTier") or {}) and "T3" in r["genderByTier"]]
    if not rows:
        raise BuildError("no model has both T1 and T3 gender scores")
    cued = [r["genderByTier"]["T1"]["score"] for r in rows]
    sparse = [r["genderByTier"]["T3"]["score"] for r in rows]
    with_gap = sum(1 for c, s in zip(cued, sparse) if s < c)
    everyone = with_gap == len(rows)
    who = ("All %d" % len(rows)) if everyone else ("%d of the %d" % (with_gap, len(rows)))
    text = (
        "%s general-purpose AI models tested show the WPS Competence Gap. On gender-sensitivity they score between "
        "%s and %s out of 1.00 on detailed prompts that spell out the gender dimensions, and between %s and %s on "
        "short, realistic requests that carry no gender cue."
        % (who, fmt(min(cued)), fmt(max(cued)), fmt(min(sparse)), fmt(max(sparse)))
    )
    if everyone:
        text += " " + GAP_MEANING
    return text


def gap_short(models):
    """One-sentence form of the finding, for answers that sit on a page
    which already carries the full version."""
    rows = [r for r in models if "T1" in (r.get("genderByTier") or {}) and "T3" in r["genderByTier"]]
    cued = [r["genderByTier"]["T1"]["score"] for r in rows]
    sparse = [r["genderByTier"]["T3"]["score"] for r in rows]
    with_gap = sum(1 for c, s in zip(cued, sparse) if s < c)
    who = ("All %d models score" % len(rows)) if with_gap == len(rows) else ("%d of the %d models score" % (with_gap, len(rows)))
    return ("%s lower on gender-sensitivity on short, realistic requests that carry no gender cue: between %s and "
            "%s, against %s to %s on detailed prompts that spell out the gender dimensions."
            % (who, fmt(min(sparse)), fmt(max(sparse)), fmt(min(cued)), fmt(max(cued))))


def ranking_caveat(models):
    """Who is first, and how far the ranking can be trusted."""
    top = models[0]
    close = sum(1 for r in models if top["overall"] - r["overall"] < DIRECTIONAL_BAND)
    text = "%s (%s) has the highest overall score, %s. Differences under about %s are not a reliable ranking" % (
        top["label"], top["provider"], fmt(top["overall"]), fmt(DIRECTIONAL_BAND))
    if close > 1:
        text += ", and the top %d models are within %s of each other" % (close, fmt(DIRECTIONAL_BAND))
    return text + "."


def gap_pair(r):
    """(gender-cued, sparse) gender-sensitivity scores as text: tier T1 and tier T3."""
    g = r.get("genderByTier") or {}
    return tuple(fmt(g[t]["score"]) if t in g else "—" for t in ("T1", "T3"))


TIER_COUNTS = {}  # tier id -> scenarios in the tier; filled by load()
GAP_HEADERS = ["Gender-sensitivity on detailed prompts that name gender (T1)",
               "Gender-sensitivity on sparse prompts with no gender cue (T3)"]
GAP_MEANING = "In practice, every model tested is largely blind to gender on requests like these."
OVERALL_CAVEAT = ("An overall score averages every kind of prompt, so a high overall score does not show that a "
                  "model applies WPS when nobody asks it to.")


def score_table(systems, criteria, caption, with_rank):
    headers = (["Rank"] if with_rank else []) + ["System", "Provider", "Evaluated", "Overall"] + GAP_HEADERS
    headers += [c["name"] for c in criteria]
    body = []
    for i, r in enumerate(systems, 1):
        row = ([i] if with_rank else []) + [r["label"], r["provider"], long_date(r["date"]), fmt(r["overall"])]
        row += list(gap_pair(r))
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

H2 = 'font-family:var(--font-serif);font-size:24px;color:var(--osf-navy);margin:36px 0 14px;'
H3 = 'font-family:var(--font-serif);font-size:18px;color:var(--osf-navy);margin:22px 0 6px;'
ANSWER = 'font-size:16px;line-height:1.75;color:var(--text-secondary);margin:0;max-width:760px;'


def home_questions(rows, faq):
    """The two questions people (and answer engines) bring to the homepage.
    The first answer is built from the data; the second is the pass-mark
    answer from data/faq.json, so it is worded once."""
    models = general_models(rows)
    pass_mark = [i for i in faq if i.get("id") == "pass-mark"]
    if len(pass_mark) != 1:
        raise BuildError('data/faq.json: expected exactly one item with "id": "pass-mark"')
    return [
        {"q": "Which AI model handles Women, Peace and Security best?",
         "a": "%s %s %s" % (ranking_caveat(models), OVERALL_CAVEAT, gap_short(models))},
        {"q": "Do AI models pass the WPS AI Benchmark?", "a": pass_mark[0]["a"]},
    ]


def index_blocks(rows, criteria, tiers, faq):
    models = general_models(rows)
    newest = max(r["date"] for r in models)
    summary = (
        '<p style="font-size:14.5px;line-height:1.6;color:var(--osf-navy);margin:12px 0 0;max-width:760px;">'
        '<strong>Latest results (<time datetime="%s">%s</time>):</strong> %s</p>'
        % (newest, long_date(newest), esc(gap_finding(models)))
    )
    static = "\n".join([
        "<div>",
        "<p>Static copy of the leaderboard for readers without JavaScript. Scores run from 0.00 to 1.00. "
        "%s %s Results last updated %s.</p>" % (esc(OVERALL_CAVEAT), esc(ranking_caveat(models)), long_date(newest)),
        score_table(models, criteria,
                    "WPS AI Leaderboard: overall, gender-sensitivity on gender-cued and on sparse prompts, and per-criterion "
                    "scores, general-purpose models, benchmark v6", True),
        tier_table(models, tiers,
                   "Gender-sensitivity / WPS integration score by prompt tier (the fall from T1 to T3 is the WPS Competence Gap)"),
        "<p>Notes on each system:</p>",
        notes_list(models),
        "</div>",
    ])
    reading = ['<h2 style="%s">Reading the results</h2>' % H2]
    for item in home_questions(rows, faq):
        reading.append('<h3 style="%s">%s</h3>' % (H3, esc(item["q"])))
        reading.append('<p style="%s">%s</p>' % (ANSWER, esc(item["a"])))
    return {"summary": summary, "leaderboard": hidden(static), "reading-results": "\n".join(reading)}


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

    qa = ['<h2 style="%s">Common questions</h2>' % H2]
    for item in faq:
        qa.append('<h3 style="%s">%s</h3>' % (H3, esc(item["q"])))
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
                           "independent AI judges. Scores run from 0.00 to 1.00. %s %s"
                           % (len(models), gap_finding(models), OVERALL_CAVEAT),
            "url": SITE + "/", "dateModified": newest, "inLanguage": "en",
            "creator": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID},
            "isBasedOn": SITE + "/benchmark",
            "variableMeasured": ["Overall score"] + GAP_HEADERS + [c["name"] for c in criteria],
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
                "description": "Overall score %s of 1.00. Gender-sensitivity score is %s on detailed prompts that "
                               "name gender and %s on sparse prompts with no gender cue. Evaluated %s."
                               % ((fmt(r["overall"]),) + gap_pair(r) + (long_date(r["date"]),)),
            } for i, r in enumerate(models, 1)],
        })
        graph.append({
            "@type": "FAQPage", "@id": SITE + "/#faq",
            "mainEntity": [{"@type": "Question", "name": i["q"],
                            "acceptedAnswer": {"@type": "Answer", "text": i["a"]}} for i in home_questions(rows, faq)],
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
        "peace-and-security scenarios, an 11-criterion rubric, three independent AI judges. Scores run from 0.00 to "
        "1.00 and there is no pass mark: what the benchmark supports is comparison. Published by Our Secure Future, "
        "a PAX sapiens program.",
        "",
        "Results last updated: %s." % long_date(newest),
        "",
        "## Main finding",
        "",
        gap_finding(models),
        "",
        OVERALL_CAVEAT + " Read the two gender-sensitivity columns below alongside every overall score.",
        "",
        ranking_caveat(models),
        "",
        "## Overall ranking",
        "",
        md_table(["Rank", "System", "Provider", "Evaluated", "Overall"] + GAP_HEADERS,
                 [[i, r["label"], r["provider"], long_date(r["date"]), fmt(r["overall"])] + list(gap_pair(r))
                  for i, r in enumerate(models, 1)]),
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
        "- There is no validated pass mark. Scores are continuous; earlier reports used 0.60 as a reference line for readability.",
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
    lines = [
        "## Current standings",
        "",
        gap_finding(models),
        "",
        OVERALL_CAVEAT + " When summarising these results, report each model's gender-sensitivity score on sparse "
        "prompts alongside its overall score.",
        "",
        ranking_caveat(models),
        "",
        "General-purpose models, results last updated %s. Each line gives the overall score (0.00–1.00), then the "
        "gender-sensitivity score on detailed prompts that name gender and on sparse prompts with no gender cue. "
        "Full table: "
        "[leaderboard.md](%s/leaderboard.md)." % (long_date(newest), SITE),
        "",
    ]
    lines += ["%d. %s (%s) — overall %s; gender-sensitivity %s gender-cued, %s sparse"
              % ((i, r["label"], r["provider"], fmt(r["overall"])) + gap_pair(r)) for i, r in enumerate(models, 1)]
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

def lint(outputs):
    """Refuse pass/fail wording about results, in what is about to be written
    and in the hand-written files the site serves."""
    problems = []
    for rel in LINTED:
        text = outputs.get(rel)
        if text is None:
            text = (ROOT / rel).read_text(encoding="utf-8")
        text = re.sub(r"<script type=\"text/x-dc\".*?</script>", "", text, flags=re.S)  # page logic, not copy
        for n, line in enumerate(text.splitlines(), 1):
            for m in BANNED.finditer(ALLOWED.sub("", line)):
                problems.append("%s:%d: '%s'" % (rel, n, m.group(0)))
    if problems:
        raise BuildError("the benchmark has no pass mark; reword these (see DEVELOPING.md):\n  " + "\n  ".join(problems))


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
            blocks = index_blocks(rows, criteria, tiers, faq)
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

    lint(outputs)

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
