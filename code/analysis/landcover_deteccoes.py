"""Classifica as detecções pela cobertura do solo (ESA WorldCover v200)."""
import json
import os
from pathlib import Path

import ee
import pandas as pd

ee.Initialize(project=os.environ.get("EE_PROJECT"))
base = Path(os.environ.get(
    "GRUEL_RAW", Path(__file__).resolve().parents[2] / "data" / "temporal"))
NUCLEO = (95.000, 24.790, 95.025, 24.818)
PERIODOS = ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22",
            "2022-23", "2023-24", "2024-25", "2025-26"]
NOMES = {10: "floresta", 20: "arbusto", 30: "gramínea", 40: "agricultura",
         50: "construído", 60: "solo exposto", 70: "neve", 80: "água",
         90: "zona úmida", 95: "mangue", 100: "musgo"}

world = ee.ImageCollection("ESA/WorldCover/v200").first().select("Map")


def classe(df):
    feats = [ee.Feature(ee.Geometry.Point([float(r.lon), float(r.lat)]),
                        {"i": int(i)})
             for i, r in enumerate(df.itertuples())]
    fc = ee.FeatureCollection(feats)
    amostra = world.sampleRegions(collection=fc, scale=10, geometries=False)
    vals = amostra.getInfo()["features"]
    mapa = {int(f["properties"]["i"]): int(f["properties"]["Map"]) for f in vals}
    return [mapa.get(i) for i in range(len(df))]


out = {}
for p in PERIODOS:
    f = base / p / "chindwin" / "scores.csv"
    if not f.exists():
        continue
    df = pd.read_csv(f)
    df = df[df.score > 0.43].copy()
    dentro = (df.lon >= NUCLEO[0]) & (df.lat >= NUCLEO[1])
    df["nucleo"] = dentro
    df["classe"] = classe(df)
    resumo = {}
    for nome, sub in (("nucleo", df[df.nucleo]), ("fora", df[~df.nucleo])):
        cont = sub.classe.value_counts(dropna=False).to_dict()
        resumo[nome] = {
            ("sem dados" if (isinstance(k, float) and k != k) or k is None
             else NOMES.get(int(k), str(k))): int(v)
            for k, v in sorted(cont.items(), key=lambda kv: -kv[1])}
    out[p] = resumo
    print(p, json.dumps(resumo, ensure_ascii=False), flush=True)

(base / "landcover_deteccoes.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
