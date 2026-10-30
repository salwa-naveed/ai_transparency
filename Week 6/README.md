# State AI Transparency Law Map, 2026

Static site (no build step). Open `index.html` through any web server, or enable GitHub Pages on the repo root.

- `index.html`, `styles.css`, `app.js`: the site
- `data/data.js`: all 115 laws from the Transparency Coalition 2026 State AI Legislation Report, with framework tags, plus enforcement notes and benchmark columns (Federal M-25-21, NY LOADinG, TX, CO) from the policy paper
- `vendor/`: d3-array, d3-geo, topojson-client and US state shapes (same as the deepfake tracker)

Framework tags (I, N, P, M, C, V; 2 = close analogue, 1 = loose) are the author's reading of the report summaries. Check bill text before citing.

## Updating the bill data
`data/outcomes.js` is generated from LegiScan bulk CSV downloads (legiscan.com/datasets, 2026 tab, "CSV Basic"):

    python3 -I tools/build_outcomes.py "/path/to/folder/with/unzipped/state/folders"

The raw LegiScan files are not in this repo (they are large and licensed CC BY 4.0 by LegiScan LLC).
