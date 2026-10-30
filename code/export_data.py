import json
import os
import shutil
from pathlib import Path

import pandas as pd

src = Path(os.environ.get(
    "GRUEL_RAW", Path(__file__).resolve().parent.parent / "data" / "temporal"))
dst = Path(__file__).resolve().parent.parent / "data"
periods = ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22",
           "2022-23", "2023-24", "2024-25", "2025-26"]
nucleo = (95.000, 24.790, 95.025, 24.818)
rows, js = [], []
for p in periods:
    s = json.loads((src / p / "chindwin" / "summary.json").read_text(encoding="utf-8"))
    df = pd.read_csv(src / p / "chindwin" / "scores.csv")
    d = df[df.score > 0.43]
    dentro = (d.lon >= nucleo[0]) & (d.lat >= nucleo[1])
    core, fora = d[dentro], d[~dentro]
    rows.append({
        "season": p.replace("-", "–"), "start": s["start"], "end": s["end"],
        "n_chips": s["n_chips"], "total_gt_043": len(d),
        "core_gt_043": len(core), "outside_gt_043": len(fora),
        "total_gt_075": s["n_pos_0.75"],
        "core_gt_075": int((core.score > 0.75).sum()),
        "outside_gt_075": int((fora.score > 0.75).sum()),
        "score_max": round(s["score_max"], 6),
        "score_p99": round(s["score_p99"], 6),
        "score_mean": round(s["score_mean"], 6),
        "elapsed_s": s["elapsed_s"],
    })
    js.append({**s, "core_gt_043": len(core), "outside_gt_043": len(fora),
               "core_gt_075": int((core.score > 0.75).sum()),
               "outside_gt_075": int((fora.score > 0.75).sum())})

pd.DataFrame(rows).to_csv(dst / "serie_temporal.csv", index=False, encoding="utf-8")
(dst / "serie_temporal.json").write_text(
    json.dumps(js, indent=1, ensure_ascii=False), encoding="utf-8")
shutil.copy(src / "landcover_deteccoes.json", dst / "landcover_deteccoes.json")
print("ok csv/json/landcover")
