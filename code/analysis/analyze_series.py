"""Analisa a série temporal do Chindwin e monta tabela + figuras.

Referência de implementação: espera as pastas ``<safra>/chindwin/`` com
``summary.json``, ``scores.csv``, ``mosaic.npz``, ``pos.geojson`` e
``iso.geojson`` produzidas por ``run_series.py``.
"""
import json
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

AQUI = Path(__file__).resolve().parent
PERIODOS = ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22",
            "2022-23", "2023-24", "2024-25", "2025-26"]
PRE = ["2017-18", "2018-19", "2019-20"]
POS = ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
AZUL = "#2b8cff"
VERMELHO = "#d62728"
VERDE = "#2f6b4f"
TERRA = "#c98a3c"
FUNDO = "#f7f5f0"
TINTA = "#1f2523"
MUTED = "#5f6a66"

# caixa do núcleo de garimpo conhecido, definida a partir da área de 2019-20
NUCLEO = (95.000, 24.790, 95.025, 24.818)


def chave(s):
    ano = s["start"][:4]
    return f"{ano}-{str(int(ano) + 1)[2:]}"


def rotulo(s):
    return chave(s).replace("-", "–")


def conta_nucleo(s):
    import pandas as pd
    pasta = AQUI / chave(s) / "chindwin" / "scores.csv"
    df = pd.read_csv(pasta)
    d = df[df.score > 0.43]
    dentro = (d.lon >= NUCLEO[0]) & (d.lat >= NUCLEO[1])
    core = d[dentro]
    fora = d[~dentro]
    return {
        "total": int(len(d)), "core": int(len(core)), "fora": int(len(fora)),
        "core_75": int((core.score > 0.75).sum()),
        "fora_75": int((fora.score > 0.75).sum()),
    }


def carrega():
    serie = []
    for p in PERIODOS:
        f = AQUI / p / "chindwin" / "summary.json"
        if f.exists():
            serie.append(json.loads(f.read_text(encoding="utf-8")))
    return serie


def tabela(serie):
    linhas = ["| Safra seca | Patches | > 0,43 total | no núcleo | fora do núcleo "
              "| > 0,75 total | no núcleo | Score máx. | p99 |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s in serie:
        c = conta_nucleo(s)
        linhas.append(
            f"| {rotulo(s)} | {s['n_chips']} | {c['total']} | {c['core']} "
            f"| {c['fora']} | {s['n_pos_0.75']} | {c['core_75']} "
            f"| {s['score_max']:.3f} | {s['score_p99']:.3f} |")
    return "\n".join(linhas)


def medias(serie):
    d = {chave(s): conta_nucleo(s) for s in serie}

    def media(ps, campo):
        vals = [d[p][campo] for p in ps if p in d]
        return float(np.mean(vals)) if vals else None

    return {
        "total": (media(PRE, "total"), media(["2020-21"], "total"), media(POS, "total")),
        "core": (media(PRE, "core"), media(["2020-21"], "core"), media(POS, "core")),
        "fora": (media(PRE, "fora"), media(["2020-21"], "fora"), media(POS, "fora")),
    }


def grafico_barras(serie, destino):
    labels = [rotulo(s) for s in serie]
    c = [conta_nucleo(s) for s in serie]
    core = np.array([x["core"] for x in c])
    fora = np.array([x["fora"] for x in c])
    total = core + fora
    x = np.arange(len(serie))

    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=200)
    fig.patch.set_facecolor(FUNDO)
    ax.set_facecolor(FUNDO)
    ax.bar(x, core, color=VERDE, alpha=0.9, edgecolor=VERDE, linewidth=0.8,
           label="núcleo de garimpo (SE)")
    ax.bar(x, fora, bottom=core, color=TERRA, alpha=0.8, edgecolor=TERRA,
           linewidth=0.8, label="fora do núcleo (campos a oeste)")
    for i, (t, k, f) in enumerate(zip(total, core, fora)):
        ax.text(i, t + 2, str(t), ha="center", va="bottom", fontsize=9,
                color=TINTA, fontweight="bold")
        if k >= 8:
            ax.text(i, k / 2, str(k), ha="center", va="center", fontsize=8,
                    color="white")
        if f >= 8:
            ax.text(i, k + f / 2, str(f), ha="center", va="center", fontsize=8,
                    color="white")
    # linha do golpe
    idx = labels.index("2020–21") + 0.5
    ax.axvline(idx, color=MUTED, linestyle=(0, (4, 3)), linewidth=1)
    ax.text(idx + 0.08, ax.get_ylim()[1] * 0.93, "golpe de Estado\n(fev. 2021)",
            fontsize=8.5, color=MUTED, va="top")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("patches detectados (48 × 48 px)", fontsize=10)
    ax.set_xlabel("safra seca (novembro–abril)", fontsize=10)
    ax.set_title("Chindwin — o aumento total vem dos campos, não do núcleo",
                 fontsize=13, color=TINTA, pad=12)
    ax.text(0, 1.015, "Sentinel-2 L1C + Cloud Score+ · ~11 × 11 km · 2.116 patches por safra",
            transform=ax.transAxes, fontsize=8.5, color=MUTED)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.grid(axis="y", color="#dcd8cd", linewidth=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#dcd8cd")
    ax.spines["bottom"].set_color("#dcd8cd")
    fig.tight_layout()
    fig.savefig(destino, facecolor=FUNDO)
    plt.close(fig)
    print("ok", destino)


def recorte(serie):
    xs, ys = [], []
    for s in serie:
        p = AQUI / f"{s['start'][:4]}-{str(int(s['start'][:4])+1)[2:]}" / "chindwin" / "pos.geojson"
        if not p.exists():
            continue
        g = gpd.read_file(p)
        if len(g):
            g = g.to_crs("EPSG:32646")
            xs += list(g.geometry.x)
            ys += list(g.geometry.y)
    if not xs:
        return None
    return min(xs) - 500, min(ys) - 500, max(xs) + 500, max(ys) + 500


def grafico_mapas(serie, destino, recorte_utm=None):
    from pyproj import Transformer
    n = len(serie)
    cols = 3
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(10, 10 * rows / cols + 0.6),
                             dpi=180)
    fig.patch.set_facecolor(FUNDO)
    axes = np.atleast_1d(axes).ravel()
    for ax in axes:
        ax.set_axis_off()
    for k, (ax, s) in enumerate(zip(axes, serie)):
        pasta = AQUI / f"{s['start'][:4]}-{str(int(s['start'][:4])+1)[2:]}" / "chindwin"
        z = np.load(pasta / "mosaic.npz", allow_pickle=True)
        rgb, (x0, y0, x1, y1) = z["rgb"], [float(v) for v in z["extent"]]
        crs = str(z["crs"])
        ax.imshow(rgb, extent=(x0, x1, y0, y1), interpolation="lanczos")
        pos = gpd.read_file(pasta / "pos.geojson")
        iso = gpd.read_file(pasta / "iso.geojson")
        if len(pos):
            pos = pos.to_crs(crs)
            ax.scatter(pos.geometry.x, pos.geometry.y, s=7, facecolor=AZUL,
                       alpha=0.35, edgecolor=AZUL, linewidth=0.2)
        if len(iso):
            iso = iso.to_crs(crs)
            ax.scatter(iso.geometry.x, iso.geometry.y, s=11, facecolor="none",
                       edgecolor=VERMELHO, linewidth=0.7)
        # caixa do núcleo de garimpo
        tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
        cx0, cy0 = tr.transform(NUCLEO[0], NUCLEO[1])
        cx1, cy1 = tr.transform(NUCLEO[2], NUCLEO[3])
        ax.add_patch(Rectangle((cx0, cy0), cx1 - cx0, cy1 - cy0,
                               fill=False, edgecolor="white", linewidth=1.1,
                               linestyle=(0, (5, 3)), zorder=6))
        if k == 0:
            ax.text(cx0, cy1, "núcleo", color="white", fontsize=7,
                    va="bottom", ha="left", zorder=7)
        if recorte_utm:
            ax.set_xlim(recorte_utm[0], recorte_utm[2])
            ax.set_ylim(recorte_utm[1], recorte_utm[3])
        c = conta_nucleo(s)
        ax.set_title(f"{rotulo(s)}  ·  {c['total']} total  ·  "
                     f"{c['core']} no núcleo", fontsize=9, color=TINTA, pad=4)
    # escala no primeiro painel
    ax0 = axes[0]
    xl, yl = ax0.get_xlim(), ax0.get_ylim()
    sx = xl[0] + 0.06 * (xl[1] - xl[0])
    sy = yl[0] + 0.06 * (yl[1] - yl[0])
    ax0.add_patch(Rectangle((sx, sy), 1000, 0.012 * (yl[1] - yl[0]),
                            facecolor="white", edgecolor="black", linewidth=0.5,
                            zorder=5))
    ax0.text(sx + 500, sy + 0.026 * (yl[1] - yl[0]), "1 km", ha="center",
             va="bottom", fontsize=7, color="white", zorder=6)
    fig.suptitle("Chindwin — a mesma zona de garimpo, safra por safra",
                 fontsize=13, color=TINTA, y=0.995)
    fig.text(0.5, 0.005, "Azul: score > 0,43 · vermelho: score > 0,75 (subconjunto) · "
             "contagem de patches de 480 m, não área nem acurácia",
             ha="center", fontsize=8, color=MUTED)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.05,
                        hspace=0.12, wspace=0.03)
    fig.savefig(destino, facecolor=FUNDO)
    plt.close(fig)
    print("ok", destino)


def distancias(a, b):
    """Distância (m) das detecções novas em b até o núcleo detectado em a."""
    import pandas as pd
    from pyproj import Transformer

    def pontos(p):
        f = AQUI / p / "chindwin" / "scores.csv"
        df = pd.read_csv(f)
        df = df[df.score > 0.43]
        df = df[(df.lon >= NUCLEO[0]) & (df.lat >= NUCLEO[1])]
        return df[["lon", "lat"]].to_numpy()

    pa, pb = pontos(a), pontos(b)
    tr = Transformer.from_crs("EPSG:4326", "EPSG:32646", always_xy=True)
    xa, ya = tr.transform(pa[:, 0], pa[:, 1])
    xb, yb = tr.transform(pb[:, 0], pb[:, 1])
    A = np.column_stack([xa, ya])
    B = np.column_stack([xb, yb])
    d = np.sqrt(((B[:, None, :] - A[None, :, :]) ** 2).sum(axis=2)).min(axis=1)
    d = np.sort(d)
    return {
        "n": len(d), "median": float(np.median(d)),
        "p90": float(np.percentile(d, 90)),
        "frac_1km": float((d < 1000).mean()),
        "frac_500m": float((d < 500).mean()),
    }


def mapa_diferenca(a, b, destino, recorte_utm=None):
    """Mapa do que mudou entre duas safras (persistente, nova, perdida)."""
    import pandas as pd
    from pyproj import Transformer

    def pontos(p):
        df = pd.read_csv(AQUI / p / "chindwin" / "scores.csv")
        df = df[df.score > 0.43]
        return {(round(r.lon, 6), round(r.lat, 6)) for r in df.itertuples()}

    pa, pb = pontos(a), pontos(b)
    ambos, so_a, so_b = pa & pb, pa - pb, pb - pa

    z = np.load(AQUI / b / "chindwin" / "mosaic.npz", allow_pickle=True)
    rgb, (x0, y0, x1, y1) = z["rgb"], [float(v) for v in z["extent"]]
    crs = str(z["crs"])
    tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)

    def xy(ps):
        lon = [p[0] for p in ps]
        lat = [p[1] for p in ps]
        return tr.transform(lon, lat)

    fig, ax = plt.subplots(figsize=(7.2, 7.2), dpi=200)
    fig.patch.set_facecolor(FUNDO)
    ax.set_facecolor(FUNDO)
    ax.imshow(rgb, extent=(x0, x1, y0, y1), interpolation="lanczos")
    for ps, cor, marker, size, rot in (
            (ambos, "#f2f2f2", "o", 10, "persistente"),
            (so_b, VERMELHO, "o", 16, "nova"),
            (so_a, AZUL, "x", 18, "perdida")):
        if ps:
            x, y = xy(ps)
            ax.scatter(x, y, s=size, c=cor, marker=marker, linewidths=0.9,
                       alpha=0.9, zorder=5,
                       label=f"{rot} ({len(ps)})")
    # caixa do núcleo de garimpo
    cx0, cy0 = tr.transform(NUCLEO[0], NUCLEO[1])
    cx1, cy1 = tr.transform(NUCLEO[2], NUCLEO[3])
    ax.add_patch(Rectangle((cx0, cy0), cx1 - cx0, cy1 - cy0,
                           fill=False, edgecolor="white", linewidth=1.2,
                           linestyle=(0, (5, 3)), zorder=6))
    ax.text(cx0, cy1, "núcleo", color="white", fontsize=8, va="bottom",
            ha="left", zorder=7)
    if recorte_utm:
        ax.set_xlim(recorte_utm[0], recorte_utm[2])
        ax.set_ylim(recorte_utm[1], recorte_utm[3])
    ax.set_axis_off()
    ax.set_title(f"Chindwin — o que mudou de {a} para {b}", fontsize=12,
                 color=TINTA, pad=8)
    ax.legend(loc="upper left", frameon=True, facecolor=FUNDO,
              edgecolor="#dcd8cd", fontsize=8.5)
    xl, yl = ax.get_xlim(), ax.get_ylim()
    sx = xl[0] + 0.06 * (xl[1] - xl[0])
    sy = yl[0] + 0.06 * (yl[1] - yl[0])
    ax.add_patch(Rectangle((sx, sy), 1000, 0.012 * (yl[1] - yl[0]),
                            facecolor="white", edgecolor="black", linewidth=0.5,
                            zorder=6))
    ax.text(sx + 500, sy + 0.026 * (yl[1] - yl[0]), "1 km", ha="center",
            va="bottom", fontsize=7, color="white", zorder=7)
    fig.tight_layout()
    fig.savefig(destino, facecolor=FUNDO)
    plt.close(fig)
    print("ok", destino)


def persistencia(a, b):
    def pontos(p):
        f = AQUI / p / "chindwin" / "scores.csv"
        if not f.exists():
            return set()
        import pandas as pd
        df = pd.read_csv(f)
        df = df[df.score > 0.43]
        df = df[(df.lon >= NUCLEO[0]) & (df.lat >= NUCLEO[1])]
        return {(round(r.lon, 6), round(r.lat, 6)) for r in df.itertuples()}
    pa, pb = pontos(a), pontos(b)
    return {
        "a": a, "b": b,
        "n_a": len(pa), "n_b": len(pb),
        "ambos": len(pa & pb), "so_a": len(pa - pb), "so_b": len(pb - pa),
    }


def main():
    serie = carrega()
    if not serie:
        print("sem summaries")
        return
    md = ["# Série temporal — Chindwin", "",
          "Mesmo bloco de ~11 × 11 km, mesma configuração (Sentinel-2 L1C + "
          "Cloud Score+, safra seca nov–abr). O **núcleo** é a caixa "
          "95,000–95,025 E / 24,790–24,818 N, definida a partir da área de "
          "garimpo já visível em 2019–20; o resto do bloco é campo, rio e "
          "vegetação.", "",
          tabela(serie), ""]
    m = medias(serie)
    md += ["## Médias", "",
           "| | Pré (2017–18 a 2019–20) | Transição (2020–21) | Pós (2021–22 a 2025–26) |",
           "|---|---:|---:|---:|"]
    rotulos = {"total": "Patches > 0,43 (total)",
               "core": "Patches > 0,43 no núcleo",
               "fora": "Patches > 0,43 fora do núcleo"}
    for k, r in rotulos.items():
        md.append(f"| {r} | {m[k][0]:.1f} | {m[k][1]:.1f} | {m[k][2]:.1f} |")
    md += ["", "## Persistência", ""]
    for a, b in (("2019-20", "2024-25"), ("2020-21", "2021-22")):
        if all((AQUI / p / "chindwin" / "scores.csv").exists() for p in (a, b)):
            d = persistencia(a, b)
            md.append(f"- **{a} → {b} (núcleo)**: {d['ambos']} patches nos dois; "
                      f"{d['so_a']} só em {a}; {d['so_b']} só em {b}.")
            dist = distancias(a, b)
            md.append(f"  - Distância das detecções de {b} ao núcleo de {a}: "
                      f"mediana {dist['median']:.0f} m; 90% em até {dist['p90']:.0f} m; "
                      f"{100*dist['frac_500m']:.0f}% a menos de 500 m e "
                      f"{100*dist['frac_1km']:.0f}% a menos de 1 km.")
    md += ["", "## Leitura", "",
           "No núcleo de garimpo, a contagem fica em 29–40 patches em todas as "
           "safras (média 32 antes e 34 depois): não há um salto claro depois "
           "de 2021. O aumento do total em 2024–25 e 2025–26 vem de 53 e 85 "
           "patches **fora** do núcleo, em campos a oeste que ficam claros na "
           "imagem. O modelo marca solo exposto; sem rótulo local, não dá para "
           "separar campo preparado de garimpo novo.",
           "",
           "Contagem de patches de 480 m com sobreposição de 50%; não é área, "
           "não é acurácia. A série mede o mesmo bloco, mas não controla "
           "disponibilidade de imagens, aerossóis, data de plantio nem "
           "mudanças de composição entre anos."]
    (AQUI / "SERIE-TEMPORAL.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    grafico_barras(serie, AQUI / "serie_temporal.png")
    rec = recorte(serie)
    grafico_mapas(serie, AQUI / "serie_mapas.png", rec)
    if all((AQUI / p / "chindwin" / "scores.csv").exists()
           for p in ("2019-20", "2024-25")):
        mapa_diferenca("2019-20", "2024-25",
                       AQUI / "diferenca_2019_2024.png", rec)


if __name__ == "__main__":
    main()
