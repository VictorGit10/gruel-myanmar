"""Gera as figuras language-neutral da série temporal do Chindwin.

As imagens não carregam título, legenda nem texto em português: os rótulos
ficam no HTML, que é trilíngue. Assim a mesma figura serve para PT, EN e FR.
"""
import json
import os
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from pyproj import Transformer

RAIZ = Path(os.environ.get(
    "GRUEL_RAW", Path(__file__).resolve().parent.parent / "data" / "temporal"))
SAIDA = Path(__file__).resolve().parent.parent / "assets"
SAIDA.mkdir(parents=True, exist_ok=True)

PERIODOS = ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22",
            "2022-23", "2023-24", "2024-25", "2025-26"]
NUCLEO = (95.000, 24.790, 95.025, 24.818)
VERDE = "#2f6b4f"
TERRA = "#c98a3c"
AZUL = "#2b8cff"
VERMELHO = "#d62728"
FUNDO = "#f7f5f0"
TINTA = "#1f2523"
MUTED = "#5f6a66"
CRS = "EPSG:32646"


def rotulo(p):
    a = p[:4]
    return f"{a}–{str(int(a) + 1)[2:]}"


def conta(p):
    df = pd.read_csv(RAIZ / p / "chindwin" / "scores.csv")
    d = df[df.score > 0.43]
    dentro = (d.lon >= NUCLEO[0]) & (d.lat >= NUCLEO[1])
    core = d[dentro]
    fora = d[~dentro]
    return {"total": len(d), "core": len(core), "fora": len(fora),
            "core75": int((core.score > 0.75).sum())}


def recorte():
    tr = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)
    xs, ys = [], []
    for p in PERIODOS:
        f = RAIZ / p / "chindwin" / "pos.geojson"
        if not f.exists():
            continue
        g = gpd.read_file(f).to_crs(CRS)
        if len(g):
            xs += list(g.geometry.x)
            ys += list(g.geometry.y)
    return min(xs) - 500, min(ys) - 500, max(xs) + 500, max(ys) + 500


def grafico_barras():
    c = [conta(p) for p in PERIODOS]
    core = np.array([x["core"] for x in c])
    fora = np.array([x["fora"] for x in c])
    total = core + fora
    x = np.arange(len(PERIODOS))

    fig, ax = plt.subplots(figsize=(10, 5.0), dpi=200)
    fig.patch.set_facecolor(FUNDO)
    ax.set_facecolor(FUNDO)
    ax.bar(x, core, color=VERDE, alpha=0.9, edgecolor=VERDE, linewidth=0.8)
    ax.bar(x, fora, bottom=core, color=TERRA, alpha=0.8, edgecolor=TERRA,
           linewidth=0.8)
    for i, (t, k, f) in enumerate(zip(total, core, fora)):
        ax.text(i, t + 2, str(t), ha="center", va="bottom", fontsize=9,
                color=TINTA, fontweight="bold")
        if k >= 8:
            ax.text(i, k / 2, str(k), ha="center", va="center", fontsize=8,
                    color="white")
        if f >= 8:
            ax.text(i, k + f / 2, str(f), ha="center", va="center", fontsize=8,
                    color="white")
    idx = PERIODOS.index("2020-21") + 0.5
    ax.axvline(idx, color=MUTED, linestyle=(0, (4, 3)), linewidth=1)
    ax.text(idx + 0.08, 116, "Feb 2021", fontsize=8.5, color=MUTED, va="top")
    ax.set_xticks(x)
    ax.set_xticklabels([rotulo(p) for p in PERIODOS], fontsize=9)
    ax.set_ylabel("patches (48 × 48 px)", fontsize=10)
    ax.set_xlabel("Nov–Apr", fontsize=10)
    ax.set_ylim(0, 125)
    ax.grid(axis="y", color="#dcd8cd", linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#dcd8cd")
    ax.spines["bottom"].set_color("#dcd8cd")
    fig.tight_layout()
    fig.savefig(SAIDA / "serie_temporal.png", facecolor=FUNDO)
    plt.close(fig)
    print("ok serie_temporal.png")


def grafico_mapas():
    rec = recorte()
    fig, axes = plt.subplots(3, 3, figsize=(10, 10), dpi=180)
    fig.patch.set_facecolor(FUNDO)
    axes = axes.ravel()
    for ax in axes:
        ax.set_axis_off()
    for k, (ax, p) in enumerate(zip(axes, PERIODOS)):
        pasta = RAIZ / p / "chindwin"
        z = np.load(pasta / "mosaic.npz", allow_pickle=True)
        rgb, (x0, y0, x1, y1) = z["rgb"], [float(v) for v in z["extent"]]
        crs = str(z["crs"])
        ax.imshow(rgb, extent=(x0, x1, y0, y1), interpolation="lanczos")
        pos = gpd.read_file(pasta / "pos.geojson").to_crs(crs)
        iso = gpd.read_file(pasta / "iso.geojson").to_crs(crs)
        ax.scatter(pos.geometry.x, pos.geometry.y, s=7, facecolor=AZUL,
                   alpha=0.35, edgecolor=AZUL, linewidth=0.2)
        ax.scatter(iso.geometry.x, iso.geometry.y, s=11, facecolor="none",
                   edgecolor=VERMELHO, linewidth=0.7)
        tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
        cx0, cy0 = tr.transform(NUCLEO[0], NUCLEO[1])
        cx1, cy1 = tr.transform(NUCLEO[2], NUCLEO[3])
        ax.add_patch(Rectangle((cx0, cy0), cx1 - cx0, cy1 - cy0,
                               fill=False, edgecolor="white", linewidth=1.1,
                               linestyle=(0, (5, 3)), zorder=6))
        ax.set_xlim(rec[0], rec[2])
        ax.set_ylim(rec[1], rec[3])
        c = conta(p)
        ax.set_title(f"{rotulo(p)}  ·  {c['total']}/{c['core']}",
                     fontsize=9, color=TINTA, pad=4)
    # barra de escala no primeiro painel
    ax0 = axes[0]
    xl, yl = ax0.get_xlim(), ax0.get_ylim()
    sx = xl[0] + 0.06 * (xl[1] - xl[0])
    sy = yl[0] + 0.06 * (yl[1] - yl[0])
    ax0.add_patch(Rectangle((sx, sy), 1000, 0.012 * (yl[1] - yl[0]),
                            facecolor="white", edgecolor="black", linewidth=0.5,
                            zorder=5))
    ax0.text(sx + 500, sy + 0.026 * (yl[1] - yl[0]), "1 km", ha="center",
             va="bottom", fontsize=7, color="white", zorder=6)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.97, bottom=0.01,
                        hspace=0.14, wspace=0.03)
    fig.savefig(SAIDA / "serie_mapas.png", facecolor=FUNDO)
    plt.close(fig)
    print("ok serie_mapas.png")


def grafico_diferenca():
    a, b = "2019-20", "2024-25"
    pa = gpd.read_file(RAIZ / a / "chindwin" / "pos.geojson")
    pb = gpd.read_file(RAIZ / b / "chindwin" / "pos.geojson")
    pa["k"] = list(zip(pa.geometry.x.round(6), pa.geometry.y.round(6)))
    pb["k"] = list(zip(pb.geometry.x.round(6), pb.geometry.y.round(6)))
    sa, sb = set(pa.k), set(pb.k)
    ambos, so_a, so_b = sa & sb, sa - sb, sb - sa

    z = np.load(RAIZ / b / "chindwin" / "mosaic.npz", allow_pickle=True)
    rgb, (x0, y0, x1, y1) = z["rgb"], [float(v) for v in z["extent"]]
    crs = str(z["crs"])
    tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    rec = recorte()

    fig, ax = plt.subplots(figsize=(7.2, 7.2), dpi=200)
    fig.patch.set_facecolor(FUNDO)
    ax.set_facecolor(FUNDO)
    ax.imshow(rgb, extent=(x0, x1, y0, y1), interpolation="lanczos")
    for ps, cor, marker, size in (
            (ambos, "#f2f2f2", "o", 10),
            (so_b, VERMELHO, "o", 16),
            (so_a, AZUL, "x", 18)):
        if ps:
            x, y = tr.transform([p[0] for p in ps], [p[1] for p in ps])
            ax.scatter(x, y, s=size, c=cor, marker=marker, linewidths=0.9,
                       alpha=0.9, zorder=5)
    cx0, cy0 = tr.transform(NUCLEO[0], NUCLEO[1])
    cx1, cy1 = tr.transform(NUCLEO[2], NUCLEO[3])
    ax.add_patch(Rectangle((cx0, cy0), cx1 - cx0, cy1 - cy0,
                           fill=False, edgecolor="white", linewidth=1.2,
                           linestyle=(0, (5, 3)), zorder=6))
    ax.set_xlim(rec[0], rec[2])
    ax.set_ylim(rec[1], rec[3])
    ax.set_axis_off()
    xl, yl = ax.get_xlim(), ax.get_ylim()
    sx = xl[0] + 0.06 * (xl[1] - xl[0])
    sy = yl[0] + 0.06 * (yl[1] - yl[0])
    ax.add_patch(Rectangle((sx, sy), 1000, 0.012 * (yl[1] - yl[0]),
                            facecolor="white", edgecolor="black", linewidth=0.5,
                            zorder=6))
    ax.text(sx + 500, sy + 0.026 * (yl[1] - yl[0]), "1 km", ha="center",
            va="bottom", fontsize=7, color="white", zorder=7)
    fig.tight_layout()
    fig.savefig(SAIDA / "diferenca_2019_2024.png", facecolor=FUNDO)
    plt.close(fig)
    print("ok diferenca_2019_2024.png")


def grafico_nucleo():
    periodos = ["2024-25", "2025-26"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), dpi=200)
    fig.patch.set_facecolor(FUNDO)
    tr = Transformer.from_crs("EPSG:4326", CRS, always_xy=True)
    cx0, cy0 = tr.transform(NUCLEO[0], NUCLEO[1])
    cx1, cy1 = tr.transform(NUCLEO[2], NUCLEO[3])
    for ax, p in zip(axes, periodos):
        pasta = RAIZ / p / "chindwin"
        z = np.load(pasta / "mosaic.npz", allow_pickle=True)
        rgb, (x0, y0, x1, y1) = z["rgb"], [float(v) for v in z["extent"]]
        ax.imshow(rgb, extent=(x0, x1, y0, y1), interpolation="lanczos")
        pos = gpd.read_file(pasta / "pos.geojson").to_crs(CRS)
        iso = gpd.read_file(pasta / "iso.geojson").to_crs(CRS)
        pos = pos[(pos.geometry.x >= cx0) & (pos.geometry.y >= cy0)]
        iso = iso[(iso.geometry.x >= cx0) & (iso.geometry.y >= cy0)]
        ax.scatter(pos.geometry.x, pos.geometry.y, s=34, facecolor=AZUL,
                   alpha=0.35, edgecolor=AZUL, linewidth=0.3)
        ax.scatter(iso.geometry.x, iso.geometry.y, s=40, facecolor="none",
                   edgecolor=VERMELHO, linewidth=0.9)
        ax.set_xlim(cx0 - 100, cx1 + 100)
        ax.set_ylim(cy0 - 100, cy1 + 100)
        ax.set_axis_off()
        ax.set_title(f"{rotulo(p)}  ·  {len(pos)}", fontsize=11)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01,
                        wspace=0.04)
    fig.savefig(SAIDA / "nucleo_2safras.png", facecolor=FUNDO)
    plt.close(fig)
    print("ok nucleo_2safras.png")


def grafico_campos():
    periodos = ["2019-20", "2021-22", "2024-25"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4), dpi=180)
    fig.patch.set_facecolor(FUNDO)
    for ax, p in zip(axes, periodos):
        pasta = RAIZ / p / "chindwin"
        z = np.load(pasta / "mosaic.npz", allow_pickle=True)
        rgb, (x0, y0, x1, y1) = z["rgb"], [float(v) for v in z["extent"]]
        crs = str(z["crs"])
        ax.imshow(rgb, extent=(x0, x1, y0, y1), interpolation="lanczos")
        pos = gpd.read_file(pasta / "pos.geojson").to_crs(crs)
        iso = gpd.read_file(pasta / "iso.geojson").to_crs(crs)
        ax.scatter(pos.geometry.x, pos.geometry.y, s=26, facecolor=AZUL,
                   alpha=0.35, edgecolor=AZUL, linewidth=0.3)
        ax.scatter(iso.geometry.x, iso.geometry.y, s=30, facecolor="none",
                   edgecolor=VERMELHO, linewidth=0.8)
        ax.set_xlim(697500, 701500)
        ax.set_ylim(2743500, 2747500)
        ax.set_axis_off()
        c = conta(p)
        ax.set_title(f"{rotulo(p)}  ·  {c['total']}", fontsize=10)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.01,
                        wspace=0.03)
    fig.savefig(SAIDA / "campos_3safras.png", facecolor=FUNDO)
    plt.close(fig)
    print("ok campos_3safras.png")


if __name__ == "__main__":
    grafico_barras()
    grafico_mapas()
    grafico_diferenca()
    grafico_nucleo()
    grafico_campos()
