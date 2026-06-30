# Audit console (React)

Interactive single-page app to navigate and audit the softmax-vs-linear
attention separation research line. It reads the **committed result JSONs**
(`results/numeric/*.json`, `results/nl/sweep_results.json`, copied into
`src/data/`) and renders them, plus an interactive rank explorer and a live
in-browser version of all seven task generators.

## Sections
- **Overview** — thesis, KPIs, the headline Gather(N) error curve.
- **Theory & rank explorer** — Theorem I (drag the linear capacity, watch the
  `1−Hm/N` floor move) and Theorem II.
- **Numeric proofs** — rank-separation table + trained-head curves.
- **Depth (multi-layer)** — rank-of-product and two-hop routing.
- **Task families (live)** — pick a family, move the difficulty sliders / seed,
  see a real prompt and its deterministically-computed answer key.
- **Haiku scaling sweep** — the degradation fingerprint, grouped by the two
  regimes, with the full instance table.
- **Repo & reproduce** — file map and commands.

## Run
```bash
npm install
npm run dev      # dev server with HMR
npm run build    # static bundle -> dist/  (base: './', works from any subpath)
npm run preview  # serve the built dist/ on :4173
```
The prebuilt `dist/` is committed, so you can serve it directly (e.g.
`npx serve dist`, or any static host) without building.

## Notes
- Charts are dependency-free SVG (`src/components/charts.jsx`) — the only runtime
  deps are React + ReactDOM.
- `src/generators.js` reimplements the Python generators' *structure* with a JS
  PRNG; previews show the task shape, not byte-identical committed instances.
- `shot.mjs` is a `playwright-core` screenshot helper used to visually verify the
  build (`SHOT_DIR=… node shot.mjs` against a running `npm run preview`).
- To refresh the embedded data after re-running experiments, re-copy the JSONs:
  `cp ../results/numeric/*.json ../results/nl/sweep_results.json src/data/` then
  rebuild.
