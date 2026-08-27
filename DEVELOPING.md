# Developing this site locally

How to run the leaderboard site on your machine, verify a change before it ships,
and recognise the failure modes that look like bugs but aren't.

## What this site is

A **static site with no build step**. There is no `package.json`, no bundler, no
generator. The HTML files are the source. `.github/workflows/deploy-pages.yml`
uploads the repository directory as-is (`path: "."`) to GitHub Pages, then purges
the Cloudflare cache. What you see in the working tree is what gets served.

Pages are rendered client-side by a small in-house framework (`support.js`,
built from `dc-runtime`). Each page holds its markup in an `<x-dc>` block and its
logic in a `<script type="text/x-dc" data-dc-script>` block defining
`class Component extends DCLogic`. The leaderboard table is driven by
`data/leaderboard.json` and `data/criteria.json`, fetched at runtime.

## Running it

Any static file server works. From the repository root:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

### You must serve over HTTP — `file://` will not work

Opening `index.html` directly by double-clicking it gives you a **page that looks
fine but has an empty leaderboard table**. This is verified behaviour, not a
guess: React still loads, the layout still renders, and the table renders zero
data rows, because the `fetch()` calls for `data/*.json` are blocked under the
`file://` origin.

If the table is empty, check the address bar says `http://localhost:...` and not
`file://`.

### It needs working internet access

`support.js` does not bundle React. On every page load it injects script tags
pointing at `unpkg.com` and boots only once they resolve:

- `react@18.3.1/umd/react.production.min.js`
- `react-dom@18.3.1/umd/react-dom.production.min.js`
- `@babel/standalone@7.29.0/babel.min.js` (loaded lazily, only for JSX imports)

Each is pinned with a Subresource Integrity hash. If `unpkg.com` is unreachable —
offline, VPN, DNS filtering, or an extension blocking CDN scripts — nothing
renders and the console shows `[dc] failed to load React or boot:`.

This applies to the live site too: production has the same runtime CDN
dependency, not just local dev.

## Verifying a change

After changing `data/leaderboard.json` or any page, confirm in the browser:

1. **The table has rows.** It should list every system, ranked by score. An empty
   table means the data fetch failed — see the failure modes below.
2. **Row count and order are right.** Rows sort by `overall` descending.
3. **A row expands.** Click *View all* on a row and confirm the detail panel
   shows the note, the standard-criteria grid, the per-tier gender breakdown, and
   the adversarial criteria. This is the part that exercises `genderByTier` and
   `adversarial`, so a malformed row usually shows up here first.
4. **Check a row you actually changed**, not just the first one.

A quick console check that the data itself is reachable and well-formed:

```js
fetch('data/leaderboard.json').then(r => r.json()).then(d => console.log(d.length, 'rows'));
fetch('data/criteria.json').then(r => r.json()).then(d => console.log(d.criteria.length, 'criteria'));
```

## Failure modes that look like bugs

**Console spam from `sidePanel.js`** — `Uncaught (in promise) Error: Could not
establish connection. Receiving end does not exist.` This comes from a browser
extension, not from this site. Ignore it, or re-test in a private window with
extensions disabled.

**`[dc-runtime] Root: {{ row.label }} never resolved — rendered as empty`**
(repeated for many fields) — the template rendered its placeholder skeleton
because the row list was empty. It means the data never arrived, so look at the
`fetch` rather than the template. Usual causes, in order of likelihood: you are
on `file://`; `data/leaderboard.json` is missing or malformed; the CDN is blocked
so the runtime never booted.

**Stale data after editing a JSON file** — the browser may serve a cached copy
(`304 Not Modified`). Hard-refresh with `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R`.
With DevTools open you can also tick *Network → Disable cache*.

**The whole table is a single grey skeleton row** — same root cause as the
`never resolved` warnings above: no data, so the placeholder renders.

## Regenerating `data/leaderboard.json`

Do not hand-edit the score fields. They are derived from the run outputs by a
generator in the companion `Weval-WPS-Eval` repository:

```
Weval-WPS-Eval/weval benchmark/Run 6/charts/build_leaderboard.py
Weval-WPS-Eval/weval benchmark/Run 6/charts/leaderboard_manifest.json
```

Verify against the currently published file without writing anything:

```bash
python3 build_leaderboard.py --check
```

This recomputes every published row from the source run data and fails if any
derived field differs. Run it before and after adding a system — it is the
guard that stops a regeneration silently changing existing numbers.

To write:

```bash
python3 build_leaderboard.py            # writes to the default leaderboard path
python3 build_leaderboard.py --out /path/to/data/leaderboard.json
```

The generator owns `overall`, `criteria`, `genderByTier` and `adversarial`. It
**preserves** the hand-written `note` and `description` fields by matching on
`published_id`, so editorial text survives regeneration. A newly added system has
no prior note and will be written with `note: null` — the generator prints which
ids these are, and they need writing by hand.

To add a system, add an entry to `leaderboard_manifest.json` (which pins the run
directory, comparison JSON, blueprint YAML, source model id, published id, label,
provider and date), then run the generator.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy-pages.yml`, which uploads
the directory to GitHub Pages and purges Cloudflare. There is no build, so a
broken file in the tree is a broken file in production. Other branches do not
deploy.

**Do not switch the repository to Pages' "Deploy from a branch" mode.** That mode
runs Jekyll, which strips paths beginning with an underscore — and every page
loads its stylesheets from `_ds/`. The current custom-workflow deploy does not
run Jekyll, which is why `_ds/` is served correctly today. If the setting ever
changes, add a `.nojekyll` file at the repository root.
