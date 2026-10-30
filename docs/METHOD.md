# Method — Chindwin temporal series

## Question

Did mining in the Chindwin block change after the February 2021 coup? The test
was exploratory: the goal was to see whether the same model, run on the same
place across dry seasons, produced a coherent signal before and after 2021.

## Study area

- Centre: **94.95 E / 24.85 N**, Chindwin, Myanmar.
- Requested polygon: a 0.045° × 0.045° box (~5 × 5 km).
- Effective mosaic: **~11.28 × 11.28 km**, because the official tiler uses
  four 552 px tiles with 12 px padding; it does not crop to the polygon.
- **2,116 patches** of 48 × 48 px (~480 m) per season, with 50% overlap.

The **core** is the box `95.000–95.025 E / 24.790–24.818 N`. It was defined from
the mining area already visible in 2019–20, before looking at the post-2021
series. It is a fixed box, not a segmentation. The rest of the block contains
fields, river, vegetation and a few roads.

## Time windows

Nine dry seasons, November–April (end exclusive):

| season | start | end |
|---|---|---|
| 2017–18 | 2017-11-01 | 2018-04-30 |
| 2018–19 | 2018-11-01 | 2019-04-30 |
| 2019–20 | 2019-11-01 | 2020-04-30 |
| 2020–21 | 2020-11-01 | 2021-04-30 |
| 2021–22 | 2021-11-01 | 2022-04-30 |
| 2022–23 | 2022-11-01 | 2023-04-30 |
| 2023–24 | 2023-11-01 | 2024-04-30 |
| 2024–25 | 2024-11-01 | 2025-04-30 |
| 2025–26 | 2025-11-01 | 2026-04-30 |

The 2020–21 season straddles the coup (1 February 2021); it is treated as a
transition season, not as pure pre- or post-coup.

## Data and model

- Sentinel-2 **L1C** (`COPERNICUS/S2_HARMONIZED`) linked to **Cloud Score+**
  (`GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`), mask `cs_cdf >= 0.6`, median of
  the window.
- Model: `48px_v4.10b-18d-20g-21a-22bc-ensemble.h5`, input 48 × 48 px, 13
  bands, normalized `/10000` and clipped to 0–1.
- Threshold: **0.43** for a detection; **0.75** for high confidence.
- Processing: Google Earth Engine, four tile requests per season, CPU only.
  One season takes ~2–2.5 min (inference plus summary/figure).
- Original pipeline and model: <https://github.com/earthrise-media/mining-detector>
  (Earth Genome, MIT).

The same configuration was used for the control (Amazon/Peru) and the Myanmar
areas in the official test; see `../README.md` and the presentation.

## Pipeline

1. `analysis/run_series.py` calls `summarize.run_area` once per season. It reads
   the region polygon, creates the four tiles, downloads the L1C + Cloud Score+
   median, cuts the 48 px chips, runs the model and writes:
   - `scores.csv` — one row per patch (score, lon, lat);
   - `pos.geojson` / `iso.geojson` — patches above 0.43 / 0.75;
   - `mosaic.npz` — RGB mosaic for the figure;
   - `summary.json` — counts, max, p99, mean, extent, timing.
2. `analysis/analyze_series.py` computes the total and core/outside counts,
   persistence and distances, and builds the figures.
3. `analysis/landcover_deteccoes.py` samples ESA WorldCover v200 at each
   detection and splits the classes into core/outside.
4. `figuras_serie.py` rebuilds the language-neutral figures from the raw
   per-season folders.
5. `export_data.py` writes `data/serie_temporal.csv` and `.json`.
6. `montar_serie.py` builds the trilingual HTML from the CSV/JSON and the
   figures. `figuras_serie.py` and `montar_serie.py` are the only scripts needed
   to rebuild the published page from the data in this repository.

## Metrics

- **Total > 0.43**: number of patches above the detection threshold.
- **Core > 0.43**: number of those patches inside the core box.
- **Outside > 0.43**: the rest.
- **> 0.75**: high-confidence subset.
- **Score max / p99 / mean**: distribution of the model score over all 2,116
  patches.

Patch counts are **not areas**. The chips overlap by 50%, so a single 480 m
cell can be counted by up to four chips. The counts are useful for a temporal
comparison of the same grid, not for estimating hectares.

## What the series shows

| season | total > 0.43 | core | outside | > 0.75 total |
|---|---:|---:|---:|---:|
| 2017–18 | 31 | 30 | 1 | 19 |
| 2018–19 | 32 | 32 | 0 | 14 |
| 2019–20 | 34 | 34 | 0 | 20 |
| 2020–21 | 48 | 37 | 11 | 17 |
| 2021–22 | 39 | 39 | 0 | 24 |
| 2022–23 | 29 | 29 | 0 | 14 |
| 2023–24 | 63 | 40 | 23 | 20 |
| 2024–25 | 88 | 35 | 53 | 34 |
| 2025–26 | 114 | 29 | 85 | 45 |

- Core: **29–40 patches** in every season; mean **32 before 2021**, **34
  after**. No clear post-2021 jump.
- Total: rises to 88 and 114, but the increase is outside the core, in fields
  to the west.
- 2024–25: 37 of the 53 outside-core patches fall on cropland in WorldCover
  (15 forest, 1 bare).
- 2025–26: 57 of the 85 outside-core patches fall on cropland (27 forest, 1
  bare).
- 2022–23 is the cleanest post-coup season: 29 patches, all in the core.

The simplest reading is that the model is responding to bare agricultural
fields in some seasons, not to a mining expansion. That is consistent with the
visual comparison of the fields in 2019–20, 2021–22 and 2024–25.

## Why this is not an accuracy measurement

- No annual ground-truth labels for Myanmar.
- One block, one model, one threshold, one seasonal window.
- The model was trained on Amazon alluvial gold; it can confuse bare fields,
  roads, burned areas and mining.
- The core box is a manual, fixed box, not a segmentation; it was defined from
  the 2019–20 cluster, which avoids fitting it to the post-2021 data but still
  involves a choice.
- Image availability, aerosol load, acquisition dates and agricultural
  calendars change between seasons.

The test can show a pattern and a limitation; it cannot attribute the pattern
to the war.

## Reproduce

The original model, Earth Engine credentials and raw mosaics are not in this
repository. To reproduce:

1. Clone <https://github.com/earthrise-media/mining-detector> and follow its
   RUNBOOK for Python/TensorFlow and Earth Engine.
2. Place the model in `repo/models/48px_v4.10b-18d-20g-21a-22bc-ensemble.h5`.
3. Put `analysis/run_series.py` in `oficial/temporal/` (next to the
   `summarize.py` wrapper) and run it with `EE_PROJECT` set.
4. Run `analysis/analyze_series.py` and `analysis/landcover_deteccoes.py` on the
   per-season folders.
5. Rebuild the figures with `figuras_serie.py` (`GRUEL_RAW` points to the
   per-season folder) and the page with `montar_serie.py`.

## Files

- `index.html` — presentation, FR default, PT/EN/FR.
- `serie-temporal.html` — temporal analysis, FR default, PT/EN/FR.
- `assets/` — neutral figures used by the page and README.
- `data/serie_temporal.csv` / `.json` — the table above.
- `data/landcover_deteccoes.json` — WorldCover classes per detection.
- `code/` — build scripts and reference implementation.
