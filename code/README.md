# Code

Scripts used to build the figures and the trilingual temporal page, plus the
reference implementation of the analysis.

## What runs from this repository

```bash
# rebuilds serie-temporal.html from data/serie_temporal.csv and assets/
python code/montar_serie.py
```

`montar_serie.py` needs only Python 3.10+, `pandas` and the files already in
`data/` and `assets/`. It embeds the images in the HTML, so the result is
self-contained.

## Scripts that need the raw per-season outputs

These scripts expect one folder per season, e.g.
`2019-20/chindwin/{summary.json,scores.csv,mosaic.npz,pos.geojson,iso.geojson}`.
That raw output is **not** in this repository (the mosaics are several MB per
season). Set `GRUEL_RAW` to the folder that contains the season folders:

```powershell
$env:GRUEL_RAW = "C:\path\to\temporal"
python code/figuras_serie.py     # regenerates assets/*.png
python code/export_data.py       # regenerates data/serie_temporal.{csv,json}
```

`figuras_serie.py` also needs `geopandas`, `matplotlib`, `numpy`, `pandas` and
`pyproj`.

## Reference implementation (`analysis/`)

The files in `analysis/` are the scripts that produced the original series.
They were run inside `oficial/temporal/`, next to the `summarize.py` wrapper and
the `repo/core` package of the Amazon Mining Watch project. They are included
for transparency, not as a turnkey package:

- `run_series.py` — runs the official inference pipeline for each dry season.
  Copy it to `oficial/temporal/` and adjust the model path / Earth Engine
  project. It imports `summarize` and `gee` from that environment.
- `analyze_series.py` — computes patch counts, core/outside split, persistence
  and the figures. It expects the per-season folders described above.
- `landcover_deteccoes.py` — samples ESA WorldCover v200 at each detection.
  Set `EE_PROJECT` and `GRUEL_RAW` before running.

The original model and pipeline are at
<https://github.com/earthrise-media/mining-detector> (MIT). The model file
(`48px_v4.10b-18d-20g-21a-22bc-ensemble.h5`) and Earth Engine credentials are
not distributed here.

## Environment used

- Python 3.11.15
- TensorFlow 2.14
- `earthengine-api`, `geopandas`, `pandas`, `numpy`, `matplotlib`, `pyproj`,
  `pypdf`
- Google Earth Engine project (`EE_PROJECT`)
- 4 tile requests per season, CPU only; ~2–2.5 min per season

## Data contract

`data/serie_temporal.csv` has one row per season:

| column | meaning |
|---|---|
| `season` | dry season label (e.g. `2019–20`) |
| `start`, `end` | date window (end exclusive) |
| `n_chips` | 48 px patches per season (2,116) |
| `total_gt_043` | patches with score > 0.43 |
| `core_gt_043` | patches inside the mining core box |
| `outside_gt_043` | patches outside the core box |
| `total_gt_075`, `core_gt_075`, `outside_gt_075` | same, score > 0.75 |
| `score_max`, `score_p99`, `score_mean` | score statistics |
| `elapsed_s` | run time |

The core box is `95.000–95.025 E / 24.790–24.818 N`, defined from the mining
area already visible in 2019–20. It is a fixed box, not a segmentation.
