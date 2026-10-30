"""Monta a página trilíngue da série temporal do Chindwin (PT/EN/FR)."""
import base64
import json
import os
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
DADOS = Path(os.environ.get("GRUEL_DATA", REPO / "data"))
CSV = DADOS / "serie_temporal.csv"
PERIODOS = ["2017-18", "2018-19", "2019-20", "2020-21", "2021-22",
            "2022-23", "2023-24", "2024-25", "2025-26"]
PRE = ["2017-18", "2018-19", "2019-20"]
POS = ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
NUCLEO = (95.000, 24.790, 95.025, 24.818)


def rotulo(p):
    a = p[:4]
    return f"{a}–{str(int(a) + 1)[2:]}"


def linha(p):
    df = pd.read_csv(CSV)
    df["season_key"] = df["season"].str.replace("–", "-", regex=False)
    return df[df["season_key"] == p].iloc[0]


def conta(p):
    r = linha(p)
    return {"total": int(r.total_gt_043), "core": int(r.core_gt_043),
            "fora": int(r.outside_gt_043), "core75": int(r.core_gt_075)}


def media(ps, campo):
    vals = [conta(p)[campo] for p in ps]
    return sum(vals) / len(vals)


def b64(nome):
    b = (REPO / "assets" / nome).read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode("ascii")


def L(pt, en, fr):
    fr = fr.replace("'", "’")
    return (f'<span lang="pt">{pt}</span><span lang="en">{en}</span>'
            f'<span lang="fr">{fr}</span>')


def tabela(lang):
    cab = {
        "pt": ("Safra seca", "Total > 0,43", "No núcleo", "Fora do núcleo", "> 0,75", "Score máx."),
        "en": ("Dry season", "Total > 0.43", "In the core", "Outside the core", "> 0.75", "Max score"),
        "fr": ("Saison sèche", "Total > 0,43", "Dans le noyau", "Hors du noyau", "> 0,75", "Score max."),
    }[lang]
    linhas = []
    for p in PERIODOS:
        r = linha(p)
        c = conta(p)
        linhas.append(
            f"<tr><td>{rotulo(p)}</td><td>{c['total']}</td>"
            f"<td class='ok'>{c['core']}</td><td class='warn'>{c['fora']}</td>"
            f"<td>{int(r.total_gt_075)}</td><td>{float(r.score_max):.3f}</td></tr>")
    return ("<table><thead><tr>" + "".join(f"<th>{h}</th>" for h in cab) +
            "</tr></thead><tbody>" + "\n".join(linhas) + "</tbody></table>")


def main():
    pre_core = media(PRE, "core")
    post_core = media(POS, "core")
    c24 = conta("2024-25")
    c25 = conta("2025-26")
    lc = json.loads((DADOS / "landcover_deteccoes.json").read_text(encoding="utf-8"))
    fora24 = lc["2024-25"]["fora"]
    fora25 = lc["2025-26"]["fora"]
    agri24 = fora24.get("agricultura", 0)
    fl24 = fora24.get("floresta", 0)
    solo24 = fora24.get("solo exposto", 0)
    agri25 = fora25.get("agricultura", 0)
    fl25 = fora25.get("floresta", 0)
    solo25 = fora25.get("solo exposto", 0)

    html = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chindwin — série temporelle</title>
<style>
:root{{--bg:#f7f5f0;--card:#fffdf9;--ink:#1f2523;--muted:#5f6a66;
--line:#dcd8cd;--accent:#2f6b4f;--accent-soft:#e6efe9;--warn:#9a6a12;--warn-soft:#f6ecd6;
--blue:#2b8cff;--red:#d62728;--green:#2f6b4f;--earth:#c98a3c}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--ink);
font:17px/1.6 "Segoe UI",system-ui,-apple-system,Roboto,sans-serif}}
html[lang="fr"] [lang="pt"],html[lang="fr"] [lang="en"],
html[lang="pt"] [lang="fr"],html[lang="pt"] [lang="en"],
html[lang="en"] [lang="fr"],html[lang="en"] [lang="pt"]{{display:none}}
main{{max-width:1080px;margin:0 auto;padding:44px 28px 60px}}
.top{{display:flex;justify-content:space-between;align-items:center;gap:16px;
margin-bottom:30px;font-size:13px}}
.top a{{color:var(--muted);text-decoration:none}}
.top a:hover{{color:var(--accent)}}
.langs{{display:flex;gap:2px;border:1px solid var(--line);border-radius:999px;padding:2px}}
.langs button{{font:inherit;font-size:12px;font-weight:700;border:0;background:none;
color:var(--muted);padding:3px 9px;border-radius:999px;cursor:pointer}}
.langs button[aria-pressed="true"]{{background:var(--accent);color:#fff}}
.kicker{{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;
color:var(--accent);margin-bottom:10px}}
h1,h2{{font-family:"Iowan Old Style","Palatino Linotype",Georgia,serif;
line-height:1.12;text-wrap:balance;margin:0 0 14px}}
h1{{font-size:clamp(32px,4.4vw,48px)}}
h2{{font-size:clamp(23px,2.8vw,31px);margin-top:40px}}
p{{margin:0 0 12px;max-width:78ch}}
.lead{{font-size:19px;color:var(--muted);max-width:72ch}}
.meta{{font-size:13px;color:var(--muted)}}
.big{{font-size:clamp(20px,2.4vw,26px);font-family:"Iowan Old Style","Palatino Linotype",Georgia,serif;
line-height:1.35;background:var(--accent-soft);border-radius:12px;padding:20px 22px;margin:24px 0}}
figure{{margin:22px 0 8px}}
figure img{{width:100%;border:1px solid var(--line);border-radius:12px;background:var(--card)}}
figcaption{{font-size:13px;color:var(--muted);margin-top:7px;line-height:1.45}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;align-items:center;font-size:13px;
color:var(--muted);margin:8px 0 0}}
.sw{{display:inline-block;width:13px;height:13px;border-radius:3px;flex:0 0 auto;margin-right:5px;
vertical-align:-2px}}
.sw-green{{background:var(--green)}}
.sw-earth{{background:var(--earth)}}
.sw-blue{{background:var(--blue);opacity:.5;border:1px solid #1f5fa8}}
.sw-red{{background:transparent;border:2px solid var(--red)}}
.sw-white{{background:#f2f2f2;border:1px solid #999}}
.sw-x{{color:var(--blue);font-weight:800}}
table{{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);
border-radius:10px;overflow:hidden;font-size:14.5px;margin:16px 0}}
th,td{{padding:8px 10px;border-bottom:1px solid var(--line);text-align:right}}
th:first-child,td:first-child{{text-align:left}}
th{{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}}
tr:last-child td{{border-bottom:0}}
td.ok{{color:var(--accent);font-weight:700}}
td.warn{{color:var(--warn);font-weight:700}}
.callout{{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);
border-radius:10px;padding:16px 18px;margin:18px 0}}
.callout.warn{{border-left-color:var(--warn);background:var(--warn-soft)}}
.callout p:last-child{{margin-bottom:0}}
ul{{max-width:78ch}}
li{{margin:0 0 7px}}
footer{{border-top:1px solid var(--line);margin-top:46px;padding-top:16px;
font-size:12px;color:var(--muted)}}
footer a{{color:var(--muted)}}
@media(max-width:700px){{main{{padding:28px 16px 44px}}}}
@media print{{body{{background:#fff}}main{{max-width:none;padding:0}}
h2{{page-break-after:avoid}}figure{{page-break-inside:avoid}}
.top .langs{{display:none}}}}
</style>
</head>
<body>
<main>
<div class="top">
  <a href="index.html">← {L("Apresentação", "Presentation", "Présentation")}</a>
  <div class="langs" role="group" aria-label="Idioma">
    <button type="button" data-l="pt" aria-pressed="false">PT</button>
    <button type="button" data-l="en" aria-pressed="false">EN</button>
    <button type="button" data-l="fr" aria-pressed="true">FR</button>
  </div>
</div>

<div class="kicker">{L("Teste exploratório · 30/10/2026", "Exploratory test · 30/10/2026", "Test exploratoire · 30/10/2026")}</div>
<h1>{L("Chindwin, safra por safra", "Chindwin, season by season", "Le Chindwin, saison par saison")}</h1>
<p class="lead">{L(
    "O mesmo bloco de ~11 × 11 km, rodado nove vezes com o modelo do Amazon Mining Watch. A pergunta era se a mineração mudou depois de 2021.",
    "The same ~11 × 11 km block, run nine times with the Amazon Mining Watch model. The question was whether mining changed after 2021.",
    "Le même bloc de ~11 × 11 km, exécuté neuf fois avec le modèle d’Amazon Mining Watch. La question était de savoir si l’exploitation minière a changé après 2021.")}</p>
<p class="meta">{L(
    "Sentinel-2 L1C + Cloud Score+ · safra seca nov–abr · modelo 48px_v4.10b-18d-20g-21a-22bc-ensemble · limiar 0,43",
    "Sentinel-2 L1C + Cloud Score+ · dry season Nov–Apr · model 48px_v4.10b-18d-20g-21a-22bc-ensemble · threshold 0.43",
    "Sentinel-2 L1C + Cloud Score+ · saison sèche nov.–avr. · modèle 48px_v4.10b-18d-20g-21a-22bc-ensemble · seuil 0,43")}</p>

<div class="big">{L(
    f"No núcleo de garimpo, a contagem fica estável: média de {pre_core:.0f} patches antes de 2021 e {post_core:.0f} depois. O total sobe porque o modelo passa a marcar campos a oeste do núcleo.",
    f"In the mining core, the count is stable: an average of {pre_core:.0f} patches before 2021 and {post_core:.0f} after. The total rises because the model starts flagging fields west of the core.",
    f"Dans le noyau de garimpo, le compte est stable : {pre_core:.0f} patches en moyenne avant 2021 et {post_core:.0f} après. Le total augmente parce que le modèle signale aussi des champs à l’ouest du noyau.")}</div>

<h2>{L("O que os números mostram", "What the numbers show", "Ce que montrent les chiffres")}</h2>
<figure><img src="{b64('serie_temporal.png')}" alt="Detections by dry season">
<figcaption>{L(
    "Verde: patches dentro da caixa do núcleo de garimpo. Laranja: patches fora dela, em campos a oeste. A linha tracejada marca fevereiro de 2021.",
    "Green: patches inside the mining core box. Orange: patches outside it, in fields to the west. The dashed line marks February 2021.",
    "Vert : patches dans la boîte du noyau de garimpo. Orange : patches hors de la boîte, dans les champs à l’ouest. La ligne en pointillés marque février 2021.")}</figcaption></figure>
<div class="legend">
  <span><span class="sw sw-green"></span>{L("núcleo de garimpo (SE)", "mining core (SE)", "noyau de garimpo (SE)")}</span>
  <span><span class="sw sw-earth"></span>{L("fora do núcleo (campos a oeste)", "outside the core (fields to the west)", "hors du noyau (champs à l’ouest)")}</span>
</div>

<div class="lang-body" lang="pt">{tabela("pt")}</div>
<div class="lang-body" lang="en">{tabela("en")}</div>
<div class="lang-body" lang="fr">{tabela("fr")}</div>

<h2>{L("Onde o modelo dispara", "Where the model fires", "Où le modèle déclenche")}</h2>
<figure><img src="{b64('serie_mapas.png')}" alt="Maps by season">
<figcaption>{L(
    "A caixa tracejada é o núcleo de garimpo já visível em 2019–20. Cada painel mostra total/núcleo. Em 2024–25 e 2025–26, os pontos novos aparecem em campos a oeste, não dentro do núcleo.",
    "The dashed box is the mining core already visible in 2019–20. Each panel shows total/core. In 2024–25 and 2025–26, new points appear in fields to the west, not inside the core.",
    "La boîte en pointillés est le noyau de garimpo déjà visible en 2019–20. Chaque panneau indique total/noyau. En 2024–25 et 2025–26, les nouveaux points apparaissent dans les champs à l’ouest, pas dans le noyau.")}</figcaption></figure>
<div class="legend">
  <span><span class="sw sw-blue"></span>{L("score > 0,43", "score > 0.43", "score > 0,43")}</span>
  <span><span class="sw sw-red"></span>{L("score > 0,75 (subconjunto)", "score > 0.75 (subset)", "score > 0,75 (sous-ensemble)")}</span>
  <span><span class="sw sw-white"></span>{L("caixa tracejada: núcleo", "dashed box: core", "boîte en pointillés : noyau")}</span>
</div>

<div class="callout warn">
<p>{L(
    f"Os totais de 2024–25 e 2025–26 enganam. Em 2024–25 são {c24['total']} patches acima de 0,43, mas {c24['fora']} estão fora do núcleo, em campos que ficam claros na imagem. Dentro do núcleo são {c24['core']}. No mapa de cobertura de 2021 (WorldCover), {agri24} desses {c24['fora']} caem em agricultura, {fl24} em floresta e {solo24} em solo exposto. Em 2025–26, são {c25['fora']} de {c25['total']} fora do núcleo, {agri25} deles em agricultura. O modelo marca solo exposto; ele não distingue campo preparado de garimpo.",
    f"The 2024–25 and 2025–26 totals are misleading. In 2024–25, {c24['total']} patches are above 0.43, but {c24['fora']} are outside the core, in fields that appear bright in the image. Inside the core there are {c24['core']}. In the 2021 land-cover map (WorldCover), {agri24} of those {c24['fora']} fall on cropland, {fl24} on forest and {solo24} on bare soil. In 2025–26, {c25['fora']} of {c25['total']} are outside the core, {agri25} of them on cropland. The model flags bare soil; it does not distinguish prepared fields from mining.",
    f"Les totaux de 2024–25 et 2025–26 sont trompeurs. En 2024–25, {c24['total']} patches dépassent 0,43, mais {c24['fora']} sont hors du noyau, dans des champs qui apparaissent clairs sur l’image. Dans le noyau, il y en a {c24['core']}. Sur la carte de couverture 2021 (WorldCover), {agri24} de ces {c24['fora']} tombent sur des cultures, {fl24} sur de la forêt et {solo24} sur du sol nu. En 2025–26, {c25['fora']} des {c25['total']} sont hors du noyau, dont {agri25} sur des cultures. Le modèle détecte le sol nu ; il ne distingue pas un champ préparé d’une mine.")}</p>
</div>

<h2>{L("O que mudou de 2019–20 para 2024–25", "What changed from 2019–20 to 2024–25", "Ce qui a changé de 2019–20 à 2024–25")}</h2>
<figure><img src="{b64('diferenca_2019_2024.png')}" alt="Difference map">
<figcaption>{L(
    "Branco: patches nos dois anos. Vermelho: novos em 2024–25. Azul: presentes só em 2019–20. A expansão vermelha a oeste está em campos.",
    "White: patches in both years. Red: new in 2024–25. Blue: present only in 2019–20. The red expansion to the west is in fields.",
    "Blanc : patches les deux années. Rouge : nouveaux en 2024–25. Bleu : présents seulement en 2019–20. L’expansion rouge à l’ouest est dans les champs.")}</figcaption></figure>
<div class="legend">
  <span><span class="sw sw-white"></span>{L("persistente (23)", "persistent (23)", "persistant (23)")}</span>
  <span><span class="sw sw-red"></span>{L("nova (65)", "new (65)", "nouveau (65)")}</span>
  <span><span class="sw sw-x">×</span>{L("perdida (11)", "lost (11)", "perdu (11)")}</span>
</div>

<h2>{L("O núcleo, duas safras", "The core, two seasons", "Le noyau, deux saisons")}</h2>
<figure><img src="{b64('nucleo_2safras.png')}" alt="Mining core in two seasons">
<figcaption>{L(
    "O mesmo recorte do núcleo: 35 patches em 2024–25 e 29 em 2025–26. A área de garimpo parece estável; o total de 114 vem dos campos ao redor.",
    "The same core crop: 35 patches in 2024–25 and 29 in 2025–26. The mining area appears stable; the total of 114 comes from the fields around it.",
    "Le même recadrage du noyau : 35 patches en 2024–25 et 29 en 2025–26. La zone minière semble stable ; le total de 114 vient des champs autour.")}</figcaption></figure>

<h2>{L("O mesmo recorte de campos, três safras", "The same field crop, three seasons", "Le même recadrage de champs, trois saisons")}</h2>
<figure><img src="{b64('campos_3safras.png')}" alt="Fields in three seasons">
<figcaption>{L(
    "Os campos ficam verdes em 2019–20 e 2021–22 e claros em 2024–25. O modelo acompanha essa mudança de cobertura, não necessariamente a mineração.",
    "The fields are green in 2019–20 and 2021–22 and pale in 2024–25. The model follows this land-cover change, not necessarily mining.",
    "Les champs sont verts en 2019–20 et 2021–22, clairs en 2024–25. Le modèle suit ce changement de couverture, pas nécessairement l’exploitation minière.")}</figcaption></figure>

<h2>{L("Leitura", "Reading", "Lecture")}</h2>
<ul>
<li>{L(
    f"No núcleo de garimpo, não há salto depois de 2021. A contagem fica em 29–40 patches em todas as safras; a média é {pre_core:.0f} antes e {post_core:.0f} depois. A área de garimpo parece estável neste bloco.",
    f"In the mining core, there is no jump after 2021. The count stays at 29–40 patches in every season; the average is {pre_core:.0f} before and {post_core:.0f} after. The mining area appears stable in this block.",
    f"Dans le noyau de garimpo, il n’y a pas de saut après 2021. Le compte reste entre 29 et 40 patches à chaque saison ; la moyenne est de {pre_core:.0f} avant et {post_core:.0f} après. La zone minière semble stable dans ce bloc.")}</li>
<li>{L(
    f"O aumento total vem de fora do núcleo. Em 2024–25, {c24['fora']} dos {c24['total']} patches estão em campos a oeste; em 2025–26, {c25['fora']} dos {c25['total']}. Em 2022–23, o total é 29 e todos estão no núcleo. É um padrão de cobertura do solo, não uma série de expansão do garimpo.",
    f"The total increase comes from outside the core. In 2024–25, {c24['fora']} of {c24['total']} patches are in fields to the west; in 2025–26, {c25['fora']} of {c25['total']}. In 2022–23, the total is 29 and all are in the core. This is a land-cover pattern, not a series of mining expansion.",
    f"L’augmentation du total vient de l’extérieur du noyau. En 2024–25, {c24['fora']} des {c24['total']} patches sont dans les champs à l’ouest ; en 2025–26, {c25['fora']} des {c25['total']}. En 2022–23, le total est de 29 et tous sont dans le noyau. C’est un motif de couverture du sol, pas une série d’expansion minière.")}</li>
<li>{L(
    "O teste não mostra que a guerra aumentou a mineração. Neste bloco, a interpretação mais simples é a oposta: o núcleo está estável. O teste também não prova que não houve aumento em outros lugares.",
    "The test does not show that the war increased mining. In this block, the simplest reading is the opposite: the core is stable. The test also does not prove that there was no increase elsewhere.",
    "Le test ne montre pas que la guerre a augmenté l’exploitation minière. Dans ce bloc, la lecture la plus simple est l’inverse : le noyau est stable. Le test ne prouve pas non plus qu’il n’y a pas eu d’augmentation ailleurs.")}</li>
<li>{L(
    "Uma contagem de patches não é área nem medida de acurácia. Os patches de 480 m se sobrepõem 50%; não há rótulos anuais para medir precisão ou revocação.",
    "A patch count is neither an area nor an accuracy measure. The 480 m patches overlap by 50%; there are no annual labels to measure precision or recall.",
    "Un compte de patches n’est ni une surface ni une mesure d’exactitude. Les patches de 480 m se chevauchent à 50 % ; il n’y a pas d’étiquettes annuelles pour mesurer la précision ou le rappel.")}</li>
</ul>

<div class="callout">
<p>{L(
    "O que seria preciso para responder à pergunta de verdade: um desenho com várias áreas de garimpo e áreas de comparação, rótulos anuais e controle de preço do ouro, migração, política e disponibilidade de imagens. Este teste é uma exploração, não uma medida de causalidade.",
    "What it would take to answer the question properly: a design with several mining areas and comparison areas, annual labels, and controls for gold prices, migration, policy and image availability. This test is an exploration, not a measure of causality.",
    "Ce qu’il faudrait pour répondre vraiment à la question : un dispositif avec plusieurs zones minières et des zones de comparaison, des étiquettes annuelles et un contrôle du prix de l’or, des migrations, des politiques et de la disponibilité des images. Ce test est une exploration, pas une mesure de causalité.")}</p>
</div>

<footer>
<p>{L(
    "Dados: Sentinel-2 L1C + Cloud Score+, Google Earth Engine · modelo do Amazon Mining Watch (Earth Genome, MIT) · análise reproduzível no repositório.",
    "Data: Sentinel-2 L1C + Cloud Score+, Google Earth Engine · Amazon Mining Watch model (Earth Genome, MIT) · reproducible analysis in the repository.",
    "Données : Sentinel-2 L1C + Cloud Score+, Google Earth Engine · modèle d’Amazon Mining Watch (Earth Genome, MIT) · analyse reproductible dans le dépôt.")}</p>
<p><a href="index.html">{L("Voltar à apresentação", "Back to the presentation", "Retour à la présentation")}</a>
 · <a href="https://github.com/VictorGit10/gruel-myanmar">GitHub</a></p>
</footer>
</main>
<script>
(function(){{
  var raiz=document.documentElement;
  var botoes=document.querySelectorAll('.langs button');
  function usar(l){{
    raiz.lang=l;
    botoes.forEach(function(b){{b.setAttribute('aria-pressed',String(b.dataset.l===l));}});
  }}
  usar('fr');
  botoes.forEach(function(b){{b.addEventListener('click',function(){{usar(b.dataset.l);}});}});
}})();
</script>
</body>
</html>
"""
    destino = REPO / "serie-temporal.html"
    destino.write_text(html, encoding="utf-8")
    print("ok", destino, len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
