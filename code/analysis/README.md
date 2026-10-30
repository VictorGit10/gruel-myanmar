# Reference analysis

These scripts produced the series. They are included for transparency, but they
are not a turnkey package: they depend on the local `oficial/temporal` wrapper
around the Amazon Mining Watch repository.

| File | Role |
|---|---|
| `run_series.py` | Runs the official inference pipeline for each dry season. Copy to `oficial/temporal/`; imports `summarize` and `gee`. |
| `analyze_series.py` | Computes counts, core/outside split, persistence and figures. Expects `<season>/chindwin/` folders. |
| `landcover_deteccoes.py` | Samples ESA WorldCover v200 at each detection. Set `EE_PROJECT` and `GRUEL_RAW`. |

The model file, Earth Engine credentials and raw mosaics are not distributed.
See `../README.md` and `../../docs/METHOD.md`.
