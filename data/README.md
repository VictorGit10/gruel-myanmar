# Data

## `serie_temporal.csv`

One row per dry season. Counts are **patches of 48 × 48 px (~480 m)** with 50%
overlap, not areas. The core box is `95.000–95.025 E / 24.790–24.818 N`,
defined from the mining area already visible in 2019–20.

| column | meaning |
|---|---|
| `season` | dry season label |
| `start`, `end` | Sentinel-2 window (end exclusive) |
| `n_chips` | patches analysed per season (2,116) |
| `total_gt_043` | patches with score > 0.43 |
| `core_gt_043` | patches inside the core box |
| `outside_gt_043` | patches outside the core box |
| `total_gt_075`, `core_gt_075`, `outside_gt_075` | same, score > 0.75 |
| `score_max`, `score_p99`, `score_mean` | score statistics |
| `elapsed_s` | run time |

## `serie_temporal.json`

Full per-season summaries, including the original `summary.json` fields and the
core/outside counts.

## `landcover_deteccoes.json`

ESA WorldCover v200 classes sampled at each detection, split into `nucleo`
(core) and `fora` (outside). Classes: `floresta`, `arbusto`, `gramínea`,
`agricultura`, `construído`, `solo exposto`, `água`, `zona úmida`.

The 2021 land-cover map is used as a reference for the land-cover type; it does
not establish what happened in 2024–25. The majority of the outside-core
detections fall on cropland, which supports the interpretation that the model
is responding to bare fields, but field validation would be needed to confirm
each case.

## What is not here

- The model file (`.h5`).
- Earth Engine credentials.
- Raw mosaics (`.npz`) and per-patch `scores.csv` (large).
- Ground-truth labels for Myanmar (none were available).

See `../docs/METHOD.md` for the full method and limits.
