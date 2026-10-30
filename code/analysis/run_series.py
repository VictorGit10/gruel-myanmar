"""Série temporal no mesmo bloco do Chindwin (L1C + Cloud Score+).

Referência de implementação. Este arquivo foi executado dentro de
``oficial/temporal/``, ao lado de ``summarize.py`` e do pacote ``repo/core``
do projeto Amazon Mining Watch. Para reproduzir, copie-o para essa pasta e
ajuste os caminhos do modelo e do Earth Engine.

Roda o pipeline oficial em safras secas sucessivas (nov–abr) e grava um
summary.json por período. Pode ser interrompido e retomado: períodos já
concluídos são pulados.
"""
import json
import sys
import traceback
from pathlib import Path

import tensorflow as tf

AQUI = Path(__file__).resolve().parent
OFICIAL = AQUI.parent
sys.path.insert(0, str(OFICIAL))

import summarize  # noqa: E402
from gee import DataConfig  # noqa: E402

PERIODOS = {
    "2017-18": ("2017-11-01", "2018-04-30"),
    "2018-19": ("2018-11-01", "2019-04-30"),
    "2019-20": ("2019-11-01", "2020-04-30"),
    "2020-21": ("2020-11-01", "2021-04-30"),
    "2021-22": ("2021-11-01", "2022-04-30"),
    "2022-23": ("2022-11-01", "2023-04-30"),
    "2023-24": ("2023-11-01", "2024-04-30"),
    "2024-25": ("2024-11-01", "2025-04-30"),
    "2025-26": ("2025-11-01", "2026-04-30"),
}


def main():
    cfg = DataConfig()
    model = tf.keras.models.load_model(summarize.MODEL, compile=False)
    for label, (start, end) in PERIODOS.items():
        outroot = AQUI / label
        summary_path = outroot / "chindwin" / "summary.json"
        if summary_path.exists():
            print(f"[skip] {label} já existe", flush=True)
            continue
        print(f"[run] {label} {start} -> {end}", flush=True)
        try:
            summarize.run_area("chindwin", start, end, cfg, model, outroot)
        except Exception:
            print(f"[erro] {label}", flush=True)
            traceback.print_exc()
            continue
        # consolida a série a cada período concluído
        serie = []
        for lab in PERIODOS:
            p = AQUI / lab / "chindwin" / "summary.json"
            if p.exists():
                serie.append(json.loads(p.read_text(encoding="utf-8")))
        (AQUI / "series.json").write_text(
            json.dumps(serie, indent=1, ensure_ascii=False), encoding="utf-8")
    print("[fim]", flush=True)


if __name__ == "__main__":
    main()
