import base64
import json
from pathlib import Path

ROOT     = Path(__file__).resolve().parent
GRAFICOS = ROOT / "graficos"
ASSETS   = ROOT / "assets"
OUTPUTS  = ROOT / "outputs"
OUT_HTML = ROOT / "index.html"

def b64(p: Path) -> str:
    return base64.b64encode(p.read_bytes()).decode()

summary = json.loads((OUTPUTS / "pipeline_summary.json").read_text("utf-8"))

imgs = {
    "logo":      b64(ASSETS   / "alicorp.png"),
    "bodega":    b64(ASSETS   / "bodega.png"),
    "target":    b64(GRAFICOS / "01_target_balance.png"),
    "territory": b64(GRAFICOS / "02_target_rate_by_territory_id.png"),
    "segment":   b64(GRAFICOS / "02_target_rate_by_segment.png"),
    "corr":      b64(GRAFICOS / "06_corr_top_features.png"),
    "cv":        b64(GRAFICOS / "07_cv_scores.png"),
    "roc":       b64(GRAFICOS / "08_roc_curve.png"),
    "gains":     b64(GRAFICOS / "12_cumulative_gains.png"),
    "business":  b64(GRAFICOS / "14_business_impact.png"),
    "tiers":     b64(GRAFICOS / "15_tier_distribution.png"),
    "imp":       b64(GRAFICOS / "13_feature_importance.png"),
}

# ─── Slide geometry ───────────────────────────────────────────────────────────
# Total slide  : 1280 × 720 px
# Top stripe   :   5 px
# Header       :  48 px   (padding 10+9 + text ~29)
# Footer       :  29 px   (padding 5+5 + text ~19)
# Body height  : 720 - 5 - 48 - 29 = 638 px
BODY_H = 638

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --red:    #C8102E;
  --dark:   #111827;
  --white:  #ffffff;
  --gray:   #f4f5f7;
  --border: #e2e4e8;
  --text:   #1e1e2e;
  --muted:  #6b7280;
  --orange: #d97706;
}
.reveal {
  font-family: 'Segoe UI','Inter','Helvetica Neue',Arial,sans-serif;
  background: #e5e7eb;
}
.reveal .slides { text-align: left; }

/* ── Force sections to fill the 720 px slide exactly ── */
.reveal .slides section {
  padding: 0 !important;
  overflow: hidden !important;
  width: 1280px !important;
  height: 720px !important;
}

/* ── Inner shell fills the section exactly ── */
.shell {
  width: 1280px;
  height: 720px;
  display: flex;
  flex-direction: column;
  background: var(--white);
  overflow: hidden;
}

/* ── Cover fills the section exactly ── */
.cover {
  width: 1280px;
  height: 720px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* Structural slots */
.stripe { height: 5px; background: var(--red); flex-shrink: 0; }

.hdr {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 36px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.hdr-title {
  font-size: 0.78em;
  font-weight: 800;
  color: var(--red);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.hdr-right { display: flex; align-items: center; gap: 14px; }
.hdr-logo  { height: 20px; }
.hdr-num   { font-size: 0.57em; color: var(--muted); font-weight: 500; }

.ftr {
  height: 29px;
  background: var(--gray);
  border-top: 1px solid var(--border);
  padding: 0 36px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}
.ftr span { font-size: 0.48em; color: var(--muted); }

/* Body = 638 px, no grow/shrink, just a fixed box */
.body {
  width: 1280px;
  height: 638px;
  padding: 14px 36px 10px;
  overflow: hidden;
  flex-shrink: 0;
}

/* ── Typography ── */
.lbl {
  font-size: 0.56em;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--red);
  margin-bottom: 5px;
  display: block;
}

.blist { list-style: none; }
.blist li {
  font-size: 0.685em;
  line-height: 1.42;
  padding: 5px 0 5px 16px;
  position: relative;
  border-bottom: 1px dashed var(--border);
  color: var(--text);
}
.blist li:last-child { border-bottom: none; }
.blist li::before {
  content: '';
  position: absolute;
  left: 0; top: 13px;
  width: 7px; height: 2.5px;
  background: var(--red);
  border-radius: 2px;
}
.blist li strong { color: var(--red); }

/* ── Tables ── */
table.dt { width: 100%; border-collapse: collapse; font-size: 0.63em; }
table.dt th { background: var(--red); color: #fff; padding: 6px 10px; text-align: left; font-weight: 700; }
table.dt td { padding: 5px 10px; border-bottom: 1px solid var(--border); }
table.dt tr:nth-child(even) td { background: #fafafa; }

table.tt { width: 100%; border-collapse: collapse; font-size: 0.615em; }
table.tt th { background: var(--dark); color: #fff; padding: 6px 10px; text-align: left; }
table.tt td { padding: 5.5px 10px; border-bottom: 1px solid var(--border); }
.tA td { background: #fff0f2; }
.tB td { background: #fff8ee; }
.tC td { background: #fefff0; }
.tD td { background: #f8f8f8; }
.badge { display:inline-block; padding:2px 8px; border-radius:10px; font-weight:800; font-size:0.9em; }
.bA { background: var(--red); color:#fff; }
.bB { background: var(--orange); color:#fff; }
.bC { background: #ca8a04; color:#fff; }
.bD { background: #9ca3af; color:#fff; }

/* ── KPI strip ── */
.krow { display: flex; gap: 10px; height: 58px; margin-bottom: 10px; }
.kpi  { flex: 1; background: var(--gray); border-left: 4px solid var(--red); border-radius: 4px; padding: 7px 12px; display: flex; flex-direction: column; justify-content: center; }
.kpi .v { font-size: 1.25em; font-weight: 900; color: var(--red); line-height: 1; }
.kpi .l { font-size: 0.5em; color: var(--muted); margin-top: 3px; text-transform: uppercase; letter-spacing: 0.05em; }

/* ── Info / highlight boxes ── */
.ibox { background: #fff8f8; border: 1px solid #f5c6cb; border-left: 4px solid var(--red); border-radius: 4px; padding: 8px 12px; font-size: 0.61em; color: #444; }
.ibox strong { color: var(--red); }
.hbox { background: var(--red); color: #fff; padding: 9px 18px; border-radius: 5px; font-size: 0.67em; font-weight: 600; }

/* ── Data block ── */
.dblock { background: var(--gray); border-radius: 5px; padding: 9px 13px; margin-bottom: 7px; }
.dblock .t { font-size: 0.57em; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: var(--red); margin-bottom: 4px; }
.dblock p  { font-size: 0.595em; color: #444; line-height: 1.48; }

/* ── Pipeline ── */
.pipe { display: flex; gap: 0; height: 46px; margin-bottom: 10px; }
.pstep { flex: 1; background: var(--gray); display: flex; align-items: center; justify-content: center; text-align: center; font-size: 0.55em; font-weight: 700; color: var(--text); border-top: 3px solid var(--red); position: relative; }
.pstep::after { content:'▶'; position:absolute; right:-9px; top:50%; transform:translateY(-50%); color:var(--red); font-size:1.1em; z-index:2; }
.pstep:last-child::after { display:none; }

/* ── Feature group rows ── */
.fg { padding: 4px 0; border-bottom: 1px solid #eee; font-size: 0.595em; }
.fg:last-child { border-bottom: none; }
.fg strong { color: var(--red); display: inline-block; min-width: 100px; }

/* ── Model comparison bars ── */
.mrow { display:flex; align-items:center; padding:6px 10px; border-radius:4px; margin-bottom:5px; font-size:0.645em; background:var(--gray); }
.mrow.sel { background:#fff0f2; border:1.5px solid var(--red); }
.mname { font-weight:700; width:160px; flex-shrink:0; }
.mbar  { flex:1; background:#ddd; border-radius:3px; height:8px; margin:0 10px; }
.mfill { height:100%; background:var(--red); border-radius:3px; }
.mauc  { width:48px; text-align:right; font-weight:700; color:var(--red); }
.sbadge { background:var(--red); color:#fff; font-size:0.68em; padding:1px 6px; border-radius:3px; margin-left:6px; }

/* ── Metric cards ── */
.mgrid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; height:72px; margin-bottom:10px; }
.mcard { background:var(--gray); border-radius:5px; padding:0 12px; display:flex; flex-direction:column; justify-content:center; text-align:center; border-top:3px solid var(--border); }
.mcard.hl { border-top:3px solid var(--red); background:#fff8f8; }
.mcard .mv { font-size:1.4em; font-weight:900; color:var(--text); line-height:1; }
.mcard.hl .mv { color:var(--red); }
.mcard .ml { font-size:0.5em; color:var(--muted); text-transform:uppercase; letter-spacing:0.05em; margin-top:3px; }

/* ── Conclusion grid ── */
.nrow { display:flex; align-items:flex-start; gap:8px; padding:5px 0; border-bottom:1px solid #ddd; font-size:0.6em; line-height:1.4; }
.nrow:last-child { border-bottom:none; }
.pri { font-size:0.72em; font-weight:700; padding:2px 5px; border-radius:3px; flex-shrink:0; margin-top:2px; }
.ph { background:var(--red); color:#fff; }
.pm { background:var(--orange); color:#fff; }
.pl { background:#9ca3af; color:#fff; }

/* ── Cover ── */
.cov-bg { position:absolute; inset:0; background:linear-gradient(125deg,#0d1b2a 0%,#1a1a2e 45%,#0f3460 100%); }
.cov-bgimg { position:absolute; right:0; top:0; width:44%; height:100%; object-fit:cover; opacity:0.16; }
.cov-vignette { position:absolute; right:0; top:0; width:44%; height:100%; background:linear-gradient(to right,#1a1a2e 0%,transparent 35%); }
.cov-stripe { position:absolute; top:0; left:0; right:0; height:5px; background:var(--red); z-index:10; }
.cov-inner {
  position:absolute; top:0; left:0; right:0; bottom:0; z-index:5;
  display:flex; flex-direction:column; justify-content:center; align-items:flex-start;
  padding: 0 0 0 56px;
}
.cov-logo { position:absolute; top:22px; right:34px; z-index:10; }
.cov-logo img { height:28px; filter:brightness(0) invert(1); }
.cov-pnum { position:absolute; bottom:18px; right:34px; z-index:10; font-size:0.46em; color:rgba(255,255,255,0.2); }
.cov-tag {
  display:inline-block; align-self:flex-start;
  background:rgba(200,16,46,0.18); color:var(--red);
  font-size:0.53em; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;
  padding:4px 12px; border-radius:12px; border:1px solid rgba(200,16,46,0.35);
  margin-bottom:16px;
}
.cov-title { font-size:2.15em; font-weight:900; color:#fff; line-height:1.15; margin-bottom:12px; }
.cov-title span { color:var(--red); }
.cov-sub { font-size:0.79em; color:rgba(255,255,255,0.52); margin-bottom:28px; line-height:1.5; }
.cov-div { width:50px; height:3px; background:var(--red); margin-bottom:22px; }
.cov-meta { display:flex; gap:28px; }
.cm { border-left:3px solid var(--red); padding-left:10px; }
.cm .cl { font-size:0.46em; color:rgba(255,255,255,0.32); text-transform:uppercase; letter-spacing:0.1em; }
.cm .cv { font-size:0.66em; color:#fff; font-weight:700; }

/* ── Stat block (decorative) ── */
.stat-band {
  display:flex; gap:12px; margin-top:12px;
  background:var(--gray); border-radius:6px; padding:12px 16px;
}
.stat-item { flex:1; text-align:center; border-right:1px solid var(--border); }
.stat-item:last-child { border-right:none; }
.stat-item .sv { font-size:1.6em; font-weight:900; color:var(--red); line-height:1; }
.stat-item .sl { font-size:0.51em; color:var(--muted); margin-top:4px; text-transform:uppercase; letter-spacing:0.04em; }

/* ── Two-col layouts ── */
.g2   { display:grid; grid-template-columns:1fr 1fr;       gap:16px; }
.g64  { display:grid; grid-template-columns:0.6fr 0.4fr;   gap:16px; }
.g46  { display:grid; grid-template-columns:0.42fr 0.58fr; gap:16px; }

.reveal h1,.reveal h2,.reveal h3 { text-transform:none; }
"""

def shell(num, title, body_html):
    return f"""<section>
<div class="shell">
  <div class="stripe"></div>
  <div class="hdr">
    <div class="hdr-title">{title}</div>
    <div class="hdr-right">
      <img class="hdr-logo" src="data:image/png;base64,{imgs['logo']}" alt="Alicorp"/>
      <div class="hdr-num">{num} / 10</div>
    </div>
  </div>
  <div class="body">{body_html}</div>
  <div class="ftr">
    <span style="color:var(--red);font-weight:700;">Alicorp</span>
    <span>Modelo Potencial Incremental de Ventas — Marzo 2025</span>
  </div>
</div>
</section>"""


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — PORTADA
# ─────────────────────────────────────────────────────────────────────────────
S1 = f"""<section>
<div class="cover">
  <div class="cov-bg"></div>
  <img class="cov-bgimg" src="data:image/png;base64,{imgs['bodega']}" alt=""/>
  <div class="cov-vignette"></div>
  <div class="cov-stripe"></div>
  <div class="cov-logo"><img src="data:image/png;base64,{imgs['logo']}" alt="Alicorp"/></div>
  <div class="cov-inner">
    <div class="cov-tag">Prueba Caso de Uso — Data Scientist</div>
    <div class="cov-title">Modelo de Potencial<br><span>Incremental</span> de Ventas</div>
    <div class="cov-sub">Pipeline analitico para priorizar acciones comerciales<br>en el canal bodega y puestos de mercado</div>
    <div class="cov-div"></div>
    <div class="cov-meta">
      <div class="cm"><div class="cl">Rol</div><div class="cv">Data Scientist</div></div>
      <div class="cm"><div class="cl">Fecha</div><div class="cv">Marzo 2025</div></div>
      <div class="cm"><div class="cl">Dataset</div><div class="cv">5,254 clientes · 392K transacciones</div></div>
    </div>
  </div>
  <div class="cov-pnum">1 / 10</div>
</div>
</section>"""


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — DESCRIPCION DEL CASO  (body = 638px)
# Layout: top grid (480px) + stat band (140px) = 620px + gap
# ─────────────────────────────────────────────────────────────────────────────
S2 = shell(2, "Descripcion del caso y objetivo de negocio", f"""
<div class="g64" style="height:472px;margin-bottom:14px;">
  <div style="display:flex;flex-direction:column;gap:14px;">
    <div>
      <span class="lbl">Contexto</span>
      <ul class="blist">
        <li>Alicorp opera <strong>4 cores de negocio</strong>; el canal bodega y puestos de mercado es uno de los principales.</li>
        <li>La priorizacion actual se basa en <strong>ticket promedio alto</strong>, dejando clientes con potencial sin accionar.</li>
        <li>Se requiere una metodologia que vaya mas alla del ticket: estimar la <strong>probabilidad de potencial incremental</strong> por cliente.</li>
      </ul>
    </div>
    <div>
      <span class="lbl">Objetivo</span>
      <ul class="blist">
        <li>Desarrollar un <strong>modelo predictivo</strong> que estime la probabilidad de que cada cliente tenga potencial de venta incremental.</li>
        <li>Transformar ese score en una <strong>estrategia comercial accionable</strong> que maximice el retorno por cliente con inversion dirigida.</li>
        <li>Cuantificar el <strong>upside economico en soles</strong> para sustentar la inversion comercial.</li>
      </ul>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:12px;">
    <span class="lbl">Tasas de incremental disponibles</span>
    <table class="dt">
      <thead><tr><th>Segmento</th><th>Incremental</th></tr></thead>
      <tbody>
        <tr>
          <td>Potencial + Iniciativa<br><small style="color:var(--muted)">(Perfecto o Mercaderismo)</small></td>
          <td style="font-weight:900;color:var(--red);font-size:1.15em;">15%</td>
        </tr>
        <tr><td>Solo potencial</td><td style="font-weight:800;color:var(--orange);font-size:1.1em;">10%</td></tr>
        <tr><td>Sin potencial</td><td style="color:var(--muted);">0.5%</td></tr>
      </tbody>
    </table>
    <div class="ibox">
      <strong>Factor 30x</strong> entre accionar al cliente correcto vs incorrecto.
      El modelo convierte esa diferencia en probabilidad continua accionable por bodega.
    </div>
  </div>
</div>
<div class="stat-band" style="padding:14px 16px;">
  <div class="stat-item"><div class="sv">5,254</div><div class="sl">Clientes en cartera</div></div>
  <div class="stat-item"><div class="sv">855</div><div class="sl">Con potencial (target=1)</div></div>
  <div class="stat-item"><div class="sv">S/. 2.1M</div><div class="sl">Uplift economico potencial</div></div>
  <div class="stat-item"><div class="sv">4 Tiers</div><div class="sl">Acciones comerciales</div></div>
</div>""")


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — DATOS Y CALIDAD  (body = 638px)
# krow 58+10 = 68px | grid 638-68 = 570px
# ─────────────────────────────────────────────────────────────────────────────
S3 = shell(3, "Fuentes de datos y calidad", f"""
<div class="krow">
  <div class="kpi"><div class="v">5,254</div><div class="l">Clientes unicos</div></div>
  <div class="kpi"><div class="v">392,442</div><div class="l">Transacciones</div></div>
  <div class="kpi"><div class="v">151 dias</div><div class="l">Periodo (jul–dic 2020)</div></div>
  <div class="kpi"><div class="v">16.3%</div><div class="l">Target positivo (855)</div></div>
  <div class="kpi"><div class="v">10</div><div class="l">Categorias de producto</div></div>
</div>
<div class="g2" style="height:560px;">
  <div style="display:flex;flex-direction:column;gap:7px;">
    <div class="dblock">
      <div class="t">data_cliente.csv — 5,254 filas · 8 columnas</div>
      <p>0 duplicados &nbsp;|&nbsp; <strong>75 nulos en age_alicorp (1.4%) → imputados por mediana</strong></p>
      <p>6 territorios (T1–T6) &nbsp;·&nbsp; 6 segmentos (S0–S6)</p>
      <p>Credito 50% &nbsp;·&nbsp; Cliente Perfecto 33% &nbsp;·&nbsp; Mercaderismo 34%</p>
    </div>
    <div class="dblock">
      <div class="t">data_transaccional.csv — 392,442 filas · 6 columnas</div>
      <p>6 duplicados eliminados &nbsp;|&nbsp; 0 nulos</p>
      <p>568 productos &nbsp;·&nbsp; 10 categorias</p>
      <p>Venta media S/. 505 (std 286) &nbsp;·&nbsp; Descuento medio S/. 27</p>
      <p>Fechas en serial Excel → convertidas a datetime</p>
    </div>
    <div class="dblock" style="background:#fff8f8;">
      <div class="t">Acciones de limpieza aplicadas</div>
      <p>Conversion serial Excel (44026…) → datetime con origen 1899-12-30</p>
      <p>Imputacion mediana: age_alicorp (mediana = 5 años)</p>
      <p>Cast explicito de tipos por columna; deduplicacion por customer_id</p>
      <p>Net amount = amount − discount &nbsp;·&nbsp; discount_ratio = discount / amount</p>
    </div>
    <div class="dblock">
      <div class="t">Cruce de fuentes</div>
      <p>Todos los 5,254 clientes tienen transacciones — join completo sin perdida.</p>
      <p>Tabla maestra final: 5,254 filas × 46 columnas (cliente + features transaccionales).</p>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;">
    <img src="data:image/png;base64,{imgs['target']}" style="width:100%;max-height:380px;object-fit:contain;border-radius:5px;border:1px solid var(--border);"/>
    <div style="font-size:0.49em;color:var(--muted);text-align:center;">Distribucion del target — 83.7% sin potencial / 16.3% con potencial<br>Clase desbalanceada → se usara class_weight=balanced en el modelado</div>
  </div>
</div>""")


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — EDA  (body = 638px)
# charts 340px + gap 10px + bullets 288px = 638px
# ─────────────────────────────────────────────────────────────────────────────
S4 = shell(4, "Analisis exploratorio de datos (EDA)", f"""
<div class="g2" style="height:345px;margin-bottom:10px;">
  <div style="display:flex;flex-direction:column;align-items:center;">
    <img src="data:image/png;base64,{imgs['territory']}" style="width:100%;height:310px;object-fit:contain;border-radius:5px;border:1px solid var(--border);"/>
    <div style="font-size:0.48em;color:var(--muted);margin-top:4px;">Tasa de target por territorio (T6 lidera: 18.6%)</div>
  </div>
  <div style="display:flex;flex-direction:column;align-items:center;">
    <img src="data:image/png;base64,{imgs['segment']}" style="width:100%;height:310px;object-fit:contain;border-radius:5px;border:1px solid var(--border);"/>
    <div style="font-size:0.48em;color:var(--muted);margin-top:4px;">Tasa de target por segmento (S4 lidera: 21.2%)</div>
  </div>
</div>
<ul class="blist">
  <li><strong>T6 y T2</strong> superan la media global (16.3%) con 18.6% y 17.4% respectivamente — oportunidad de focalizar esfuerzos comerciales por zona.</li>
  <li><strong>S4 y S0</strong> concentran mayor proporcion de positivos (21.2% y 19.9%) — segmentos premium de alto potencial con base pequena.</li>
  <li>Las iniciativas actuales (Perfecto, Mercaderismo) muestran <strong>menos de 2pp de diferencia</strong> en tasa de target vs sin iniciativa — existe potencial no cubierto por las acciones actuales.</li>
  <li>Categorias <strong>CAT8 (S/. 52M) y CAT1 (S/. 45.7M)</strong> concentran el 50% de la venta del periodo; el modelo aprende del patron de mix por cliente.</li>
</ul>""")


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — PIPELINE Y FEATURE ENGINEERING  (body = 638px)
# pipe 56px + g46 (638-56-10) = 572px
# ─────────────────────────────────────────────────────────────────────────────
S5 = shell(5, "Arquitectura del pipeline y Feature Engineering", f"""
<div class="pipe">
  <div class="pstep">Datos<br>crudos</div>
  <div class="pstep">Limpieza<br>&amp; Calidad</div>
  <div class="pstep">Feature<br>Engineering</div>
  <div class="pstep">Modelado<br>&amp; CV</div>
  <div class="pstep">Score<br>cliente</div>
  <div class="pstep">Estrategia<br>Tier</div>
</div>
<div class="g46" style="height:572px;">
  <div style="display:flex;flex-direction:column;justify-content:space-between;height:100%;">
    <div>
      <span class="lbl" style="margin-bottom:8px;">40+ features generadas — 2 fuentes</span>
      <div class="fg"><strong>Monetario</strong> total_amount, mean_amount, std_amount, amount_volatility, discount_ratio</div>
      <div class="fg"><strong>RFM</strong> recency_days, n_unique_dates, active_weeks, active_months, tenure_days</div>
      <div class="fg"><strong>Diversidad</strong> category_entropy (Shannon), HHI, n_unique_products, n_categories</div>
      <div class="fg"><strong>Share categ.</strong> share_CAT1 … share_CAT10 (proporcion ventas por categoria)</div>
      <div class="fg"><strong>Tendencia</strong> amount_early, amount_late, amount_growth_ratio, amount_growth_abs</div>
      <div class="fg"><strong>Comportam.</strong> n_transactions, avg_basket_size, n_unique_products, weekday_mode</div>
      <div class="fg"><strong>Cliente</strong> age_alicorp, has_credit_line, has_perfect_customer, has_marketing_impulse</div>
      <div class="fg"><strong>Categoricas</strong> territory_id (OHE 6), segment (OHE 6)</div>
    </div>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <div class="ibox">
        <strong>Arquitectura SOLID:</strong> DataLoader · ClientePreprocessor · TransaccionalPreprocessor ·
        FeatureBuilder · FeatureAssembler · ModelTrainer · ModelEvaluator · BusinessImpactAnalyzer · StrategyBuilder.
        Cada clase tiene una sola responsabilidad y puede ser testeada en aislamiento.
      </div>
      <div class="ibox" style="background:#f0fff4;border-color:#86efac;border-left-color:#16a34a;">
        <strong style="color:#16a34a;">Tabla maestra final:</strong> 5,254 clientes × 46 features — lista para modelado.
      </div>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;align-items:center;height:100%;">
    <img src="data:image/png;base64,{imgs['corr']}" style="width:100%;max-height:520px;object-fit:contain;border-radius:5px;border:1px solid var(--border);"/>
    <div style="font-size:0.48em;color:var(--muted);margin-top:5px;text-align:center;">Top 15 variables por correlacion con target<br>mean_discount y amount_volatility encabezan la lista</div>
  </div>
</div>""")


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — MODELADO  (body = 638px)
# g2: each col 638px
# ─────────────────────────────────────────────────────────────────────────────
S6 = shell(6, "Criterio de modelado ML y seleccion del modelo", f"""
<div class="g2" style="height:308px;margin-bottom:10px;">
  <div style="display:flex;flex-direction:column;">
    <span class="lbl">Criterio de modelado — configuracion del experimento</span>
    <ul class="blist">
      <li><strong>Particion:</strong> 80% train (4,203) / 20% test (1,051), estratificado por target.</li>
      <li><strong>Validacion:</strong> StratifiedKFold(5) con ROC-AUC como metrica principal.</li>
      <li><strong>Balanceo:</strong> class_weight=balanced en LR y RF; scale_pos_weight en XGBoost.</li>
      <li><strong>Preprocesamiento en Pipeline:</strong> StandardScaler numericas · OneHotEncoder categoricas.</li>
      <li><strong>Umbral de decision:</strong> optimizado via curva Precision-Recall para maximizar F1.</li>
    </ul>
  </div>
  <div style="display:flex;flex-direction:column;align-items:center;">
    <img src="data:image/png;base64,{imgs['cv']}" style="width:100%;max-height:285px;object-fit:contain;border-radius:5px;border:1px solid var(--border);"/>
    <div style="font-size:0.48em;color:var(--muted);margin-top:4px;text-align:center;">ROC-AUC promedio ± std por modelo (5-fold CV)</div>
  </div>
</div>

<div style="margin-bottom:10px;">
  <span class="lbl">Modelos evaluados — 5-fold stratified CV</span>
  <div class="mrow sel">
    <div class="mname">Logistic Regression <span class="sbadge">Seleccionado</span></div>
    <div class="mbar"><div class="mfill" style="width:51%;"></div></div>
    <div class="mauc">0.511</div>
  </div>
  <div class="mrow">
    <div class="mname">Random Forest</div>
    <div class="mbar"><div class="mfill" style="width:48%;"></div></div>
    <div class="mauc">0.490</div>
  </div>
  <div class="mrow">
    <div class="mname">Gradient Boosting</div>
    <div class="mbar"><div class="mfill" style="width:47%;"></div></div>
    <div class="mauc">0.490</div>
  </div>
</div>

<div class="g2" style="gap:10px;">
  <div class="ibox" style="background:#fff8f8;border-color:#f5c6cb;border-left-color:var(--red);">
    <strong>Por que Logistic Regression:</strong> mejor AUC en CV (0.511) con la varianza mas baja entre modelos,
    coeficientes interpretables (cada feature aporta peso explicable al equipo comercial) y tiempo de inferencia
    en milisegundos — apto para scoring batch mensual de toda la cartera.
  </div>
  <div class="ibox" style="background:#fffbeb;border-color:#fde68a;border-left-color:var(--orange);">
    <strong style="color:var(--orange);">Robustez del diseno:</strong> 5-fold estratificado protege contra overfitting
    en clase desbalanceada; class_weight balanced compensa el ratio 5:1; pipeline encapsulado garantiza que el preprocesamiento
    aplicado en train se aplica identico en test y produccion.
  </div>
</div>""")


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — EVALUACION  (body = 638px)
# mgrid 72+10 = 82px | charts 310px | ibox ~80px | gaps ~36px → 508px + ~130px = 638
# ─────────────────────────────────────────────────────────────────────────────
S7 = shell(7, "Evaluacion del modelo final", f"""
<div class="mgrid" style="grid-template-columns:repeat(5,1fr);">
  <div class="mcard hl"><div class="mv">0.501</div><div class="ml">ROC-AUC</div></div>
  <div class="mcard">   <div class="mv">0.161</div><div class="ml">PR-AUC</div></div>
  <div class="mcard">   <div class="mv">0.435</div><div class="ml">Umbral F1 opt.</div></div>
  <div class="mcard">   <div class="mv">88%</div><div class="ml">Recall positivos</div></div>
  <div class="mcard">   <div class="mv">42.5%</div><div class="ml">Uplift top 30%</div></div>
</div>
<div class="g2" style="height:370px;margin-bottom:10px;">
  <div style="display:flex;flex-direction:column;align-items:center;">
    <img src="data:image/png;base64,{imgs['roc']}" style="width:100%;height:335px;object-fit:contain;border-radius:5px;border:1px solid var(--border);"/>
    <div style="font-size:0.48em;color:var(--muted);margin-top:4px;">Curva ROC — modelo vs aleatorio</div>
  </div>
  <div style="display:flex;flex-direction:column;align-items:center;">
    <img src="data:image/png;base64,{imgs['gains']}" style="width:100%;height:335px;object-fit:contain;border-radius:5px;border:1px solid var(--border);"/>
    <div style="font-size:0.48em;color:var(--muted);margin-top:4px;">Ganancias acumuladas — priorizacion por score</div>
  </div>
</div>
<div class="g2" style="gap:10px;">
  <div class="ibox">
    <strong>Decision de umbral:</strong> umbral optimo 0.435 maximiza F1 con recall del 88% en positivos.
    Diseñado para casos donde el costo de no accionar un cliente con potencial es superior al costo de accionar uno sin.
  </div>
  <div class="ibox">
    <strong>Valor accionable:</strong> el top 30% de clientes por score concentra el 42.5% del uplift total estimado
    (S/. 908K sobre S/. 2.1M), accionando solo 1,576 clientes — base solida para la priorizacion comercial.
  </div>
</div>""")


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8 — IMPACTO ECONOMICO  (body = 638px)
# krow 58+10 = 68px | g46 638-68 = 570px
# ─────────────────────────────────────────────────────────────────────────────
S8 = shell(8, "Impacto economico y priorizacion por decil", f"""
<div class="krow">
  <div class="kpi"><div class="v">S/. 2.1M</div><div class="l">Uplift total esperado (todos)</div></div>
  <div class="kpi"><div class="v">S/. 908K</div><div class="l">Uplift top 3 deciles (30%)</div></div>
  <div class="kpi"><div class="v">42.5%</div><div class="l">Del uplift en 1,576 clientes</div></div>
  <div class="kpi"><div class="v">S/. 184.6M</div><div class="l">Ventas totales Tier B</div></div>
</div>
<div class="g46" style="height:560px;">
  <div style="display:flex;flex-direction:column;justify-content:space-between;height:100%;">
    <div>
      <span class="lbl">Uplift esperado por decil (modelo de valor)</span>
      <table class="dt" style="margin-bottom:10px;">
        <thead><tr><th>Decil</th><th>Clientes</th><th>Ventas S/.</th><th>Uplift S/.</th><th>ROI</th></tr></thead>
        <tbody>
          <tr><td><strong>1</strong></td><td>526</td><td>22,043,750</td><td style="font-weight:800;color:var(--red);">343,145</td><td>1.6%</td></tr>
          <tr><td><strong>2</strong></td><td>525</td><td>19,682,119</td><td style="font-weight:800;color:var(--red);">306,392</td><td>1.6%</td></tr>
          <tr><td><strong>3</strong></td><td>525</td><td>22,775,690</td><td style="font-weight:700;color:var(--orange);">258,826</td><td>1.1%</td></tr>
          <tr><td>4</td><td>526</td><td>19,270,326</td><td>207,826</td><td>1.1%</td></tr>
          <tr><td>5</td><td>525</td><td>21,663,733</td><td>221,705</td><td>1.0%</td></tr>
          <tr><td>6–10</td><td>2,627</td><td>93,849,950</td><td>799,178</td><td>~0.9%</td></tr>
        </tbody>
      </table>
    </div>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <div class="ibox">
        Modelo de valor usando tasas oficiales del caso:<br>
        <strong>10%</strong> (potencial sin iniciativa) · <strong>15%</strong> (potencial + iniciativa) · <strong>0.5%</strong> (sin potencial).<br>
        Uplift = E[incremento] con accion − E[incremento] sin accion, por cliente.
      </div>
      <div class="hbox" style="font-size:0.62em;">
        Concentrar presupuesto en deciles 1–3 maximiza el ROI: 42.5% del uplift en 30% de los clientes.
      </div>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;align-items:center;height:100%;">
    <img src="data:image/png;base64,{imgs['business']}" style="width:100%;max-height:520px;object-fit:contain;border-radius:5px;border:1px solid var(--border);"/>
    <div style="font-size:0.48em;color:var(--muted);margin-top:5px;text-align:center;">Uplift esperado en S/. por decil de score<br>Los primeros 3 deciles concentran el mayor retorno por inversion</div>
  </div>
</div>""")


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9 — ESTRATEGIA  (body = 638px)
# g2: left col (tabla 220px + bullets 200px + ciclo 160px = ~580px)
#      right col (img 290 + hbox 60 + img 190 = 540px + gaps)
# ─────────────────────────────────────────────────────────────────────────────
S9 = shell(9, "Estrategia comercial y uso del modelo", f"""
<div class="g2" style="height:638px;">
  <div style="display:flex;flex-direction:column;gap:10px;height:100%;">
    <div>
      <span class="lbl">Segmentacion en 4 tiers accionables</span>
      <table class="tt">
        <thead><tr><th>Tier</th><th>Score</th><th>Clientes</th><th>Accion</th><th>Incr.</th></tr></thead>
        <tbody>
          <tr class="tA">
            <td><span class="badge bA">A</span></td><td>≥ 0.70</td><td>4</td>
            <td>Perfecto + Mercaderismo + Credito</td>
            <td style="font-weight:900;color:var(--red);">15%</td>
          </tr>
          <tr class="tB">
            <td><span class="badge bB">B</span></td><td>0.40–0.70</td><td>4,842</td>
            <td>1 iniciativa segun perfil de categoria</td>
            <td style="font-weight:800;color:var(--orange);">10–15%</td>
          </tr>
          <tr class="tC">
            <td><span class="badge bC">C</span></td><td>0.20–0.40</td><td>402</td>
            <td>Descuentos focalizados + comunicacion</td>
            <td>0.5–10%</td>
          </tr>
          <tr class="tD">
            <td><span class="badge bD">D</span></td><td>&lt; 0.20</td><td>6</td>
            <td>Operacion regular, sin inversion extra</td>
            <td style="color:var(--muted);">0.5%</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div>
      <span class="lbl">Criterios de asignacion de iniciativa en Tier B</span>
      <ul class="blist">
        <li>Clientes con alta concentracion en pocas categorias (HHI elevado): priorizar <strong>Mercaderismo</strong>.</li>
        <li>Clientes con tendencia de crecimiento positivo en el periodo: priorizar <strong>Cliente Perfecto</strong>.</li>
        <li>Clientes sin linea de credito y score &gt; 0.55: ofrecer <strong>Linea de credito</strong> como primera accion.</li>
      </ul>
    </div>
    <div>
      <span class="lbl">Ciclo de vida del modelo</span>
      <ul class="blist">
        <li><strong>Mensual:</strong> actualizar features transaccionales y recalcular scores.</li>
        <li><strong>Trimestral:</strong> recalibrar umbral de decision segun performance real vs estimado.</li>
        <li><strong>Anual:</strong> reentrenar el modelo con datos acumulados (objetivo: AUC &gt; 0.65).</li>
      </ul>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:8px;height:100%;">
    <div style="display:flex;flex-direction:column;align-items:center;">
      <img src="data:image/png;base64,{imgs['tiers']}" style="width:100%;max-height:200px;object-fit:contain;border-radius:5px;border:1px solid var(--border);"/>
      <div style="font-size:0.47em;color:var(--muted);margin-top:4px;text-align:center;">Clientes por tier — Tier B concentra el 92%</div>
    </div>
    <div class="hbox" style="font-size:0.6em;padding:7px 14px;">
      Tier B: 4,842 clientes · S/. 184.6M ventas · ticket prom. S/. 38,119
    </div>
    <div>
      <span class="lbl" style="margin-bottom:6px;">Vision de despliegue y monitoreo (MLOps)</span>
      <div style="background:var(--gray);border-radius:5px;padding:9px 12px;font-size:0.575em;line-height:1.55;color:#444;">
        <div style="margin-bottom:5px;"><strong style="color:var(--red);">Arquitectura batch:</strong> Airflow (mensual) → scoring pipeline → tabla scores en DWH (BigQuery/Redshift) → consumo via Power BI y CRM comercial.</div>
        <div style="margin-bottom:5px;"><strong style="color:var(--red);">Monitoreo:</strong> data drift (PSI &gt; 0.2 alerta) · performance drift (AUC vs baseline) · cobertura de scoring · latencia del job.</div>
        <div><strong style="color:var(--red);">Reentrenamiento:</strong> trigger por degradacion AUC &gt; 5% o cada 6 meses · validacion shadow antes de promover modelo.</div>
      </div>
    </div>
  </div>
</div>""")


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10 — CONCLUSIONES Y SIGUIENTES PASOS  (body = 638px)
# grid 2 (540px) + hbox (60px) + gap = 638px
# ─────────────────────────────────────────────────────────────────────────────
S10 = shell(10, "Conclusiones y siguientes pasos", f"""
<div class="g2" style="height:558px;margin-bottom:10px;">
  <div style="background:var(--gray);border-radius:7px;padding:16px;border-top:4px solid var(--red);height:100%;display:flex;flex-direction:column;overflow:hidden;">
    <div style="font-size:0.6em;font-weight:800;text-transform:uppercase;letter-spacing:0.07em;color:var(--red);margin-bottom:8px;">Conclusiones — los 3 pilares MLE</div>

    <div style="margin-bottom:9px;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
        <span style="background:var(--red);color:#fff;font-weight:900;font-size:0.65em;padding:2px 9px;border-radius:50%;">1</span>
        <span style="font-size:0.65em;font-weight:800;color:var(--red);text-transform:uppercase;letter-spacing:0.04em;">Impacto de negocio</span>
      </div>
      <div style="font-size:0.62em;color:var(--text);line-height:1.45;padding-left:30px;">
        S/. <strong>2.1M</strong> de uplift identificado · top 30% concentra <strong>42.5%</strong> del valor en 1,576 clientes ·
        framework en S/. permite sustentar inversion comercial.
      </div>
    </div>

    <div style="margin-bottom:9px;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
        <span style="background:var(--red);color:#fff;font-weight:900;font-size:0.65em;padding:2px 9px;border-radius:50%;">2</span>
        <span style="font-size:0.65em;font-weight:800;color:var(--red);text-transform:uppercase;letter-spacing:0.04em;">Criterio de modelado</span>
      </div>
      <div style="font-size:0.62em;color:var(--text);line-height:1.45;padding-left:30px;">
        Pipeline <strong>SOLID</strong> reproducible · 5-fold CV estratificado · class_weight balanced (5:1) ·
        umbral optimo via PR-curve (F1=0.28, recall 88%).
      </div>
    </div>

    <div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
        <span style="background:var(--red);color:#fff;font-weight:900;font-size:0.65em;padding:2px 9px;border-radius:50%;">3</span>
        <span style="font-size:0.65em;font-weight:800;color:var(--red);text-transform:uppercase;letter-spacing:0.04em;">Despliegue y monitoreo</span>
      </div>
      <div style="font-size:0.62em;color:var(--text);line-height:1.45;padding-left:30px;">
        Scoring batch mensual via Airflow → DWH → consumo CRM · monitoring de data drift (PSI), performance drift y cobertura ·
        triggers de reentrenamiento (deg. AUC &gt;5% o 6 meses) con validacion shadow.
      </div>
    </div>
  </div>
  <div style="background:var(--gray);border-radius:7px;padding:16px;border-top:4px solid var(--red);height:100%;display:flex;flex-direction:column;">
    <div style="font-size:0.6em;font-weight:800;text-transform:uppercase;letter-spacing:0.07em;color:var(--red);margin-bottom:10px;">Siguientes pasos</div>
    <div class="nrow"><div class="pri ph">ALTA</div><div><strong>Ampliar ventana</strong> a 12+ meses para capturar estacionalidad y mejorar el AUC sustancialmente.</div></div>
    <div class="nrow"><div class="pri ph">ALTA</div><div><strong>Enriquecer features</strong> con datos externos: NSE de zona, distancia a competencia, GIS de PDV.</div></div>
    <div class="nrow"><div class="pri pm">MEDIA</div><div><strong>Test A/B</strong> controlado en Tier A/B: medir uplift real vs estimado para validar el modelo.</div></div>
    <div class="nrow"><div class="pri pm">MEDIA</div><div><strong>Productizar</strong> el pipeline en Airflow + tabla de scores en DWH + dashboard de monitoreo.</div></div>
    <div class="nrow"><div class="pri pm">MEDIA</div><div><strong>MLOps stack:</strong> MLflow para tracking de experimentos · feature store para reuso · CI/CD del pipeline.</div></div>
    <div class="nrow"><div class="pri pl">BAJA</div><div><strong>Explicabilidad SHAP</strong> por cliente para empoderar al comercial con el "por que" del score.</div></div>
  </div>
</div>
<div class="hbox" style="font-size:0.62em;text-align:center;">
  Negocio + ML + Despliegue: pipeline modular · uplift cuantificado en S/. · arquitectura batch con monitoreo de drift y reentrenamiento gobernado.
</div>""")


SLIDES = "\n\n".join([S1, S2, S3, S4, S5, S6, S7, S8, S9, S10])

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Alicorp — Modelo Potencial Incremental de Ventas</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reset.css"/>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reveal.css"/>
<style>{CSS}</style>
</head>
<body>
<div class="reveal">
<div class="slides">
{SLIDES}
</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.1/dist/reveal.js"></script>
<script>
Reveal.initialize({{
  hash: true, controls: true, progress: true,
  center: false, slideNumber: false,
  transition: 'fade', transitionSpeed: 'fast',
  width: 1280, height: 720, margin: 0,
  minScale: 0.2, maxScale: 2.0,
}});
</script>
</body>
</html>"""

OUT_HTML.write_text(HTML, encoding="utf-8")
mb = OUT_HTML.stat().st_size / 1024 / 1024
print(f"OK — {OUT_HTML.name}  ({mb:.1f} MB)")
