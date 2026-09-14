"""
Embudo de Admisiones — Demo con datos ficticios
App en Streamlit, sin conexión externa (datos de ejemplo incluidos en el código).

Ejecutar localmente:
    pip install -r requirements.txt
    streamlit run app_demo.py
"""

import html
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Embudo de Admisiones — Demo",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Estilos (mismo look oscuro / panel que la versión anterior)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(120% 140% at 10% 0%, #2B1A3D 0%, #1E1230 55%, #120A1E 100%);
        }
        .block-container { padding-top: 2.5rem; max-width: 1100px; }
        h1, h2, h3, p, span, label, div { color: #EAF0EE; }
        .panel-title { font-size: 20px; font-weight: 600; margin-bottom: 2px; }
        .panel-sub { font-size: 13px; color: #9FB2BB; margin-bottom: 14px; }
        .legend-row { display:flex; gap:18px; font-size:12.5px; color:#9FB2BB; margin-bottom: 10px; }
        .legend-dot { display:inline-block; width:10px; height:10px; border-radius:3px; margin-right:6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Datos ficticios
# ---------------------------------------------------------------------------
data = [
    {"sede": "Bogotá",          "programa": "Medicina",                        "value": 120},
    {"sede": "Medellín",        "programa": "Enfermería",                      "value": 95},
    {"sede": "Cali",            "programa": "Odontología",                     "value": 80},
    {"sede": "Bogotá",          "programa": "Psicología",                      "value": 68},
    {"sede": "Barranquilla",    "programa": "Administración de Empresas",      "value": 55},
    {"sede": "Medellín",        "programa": "Derecho",                         "value": 47},
    {"sede": "Cali",            "programa": "Contaduría Pública",              "value": 39},
    {"sede": "Bogotá",          "programa": "Ingeniería de Sistemas",          "value": 33},
    {"sede": "Pasto",           "programa": "Medicina Veterinaria",            "value": 28},
    {"sede": "Barranquilla",    "programa": "Nutrición y Dietética",           "value": 21},
    {"sede": "Cali",            "programa": "Publicidad y Mercadeo",           "value": 16},
    {"sede": "Medellín",        "programa": "Optometría",                      "value": 12},
    {"sede": "Bogotá",          "programa": "Negocios Internacionales",        "value": 8},
    {"sede": "Pasto",           "programa": "Fisioterapia",                    "value": 4},
]

df = pd.DataFrame(data)

# Orden ascendente: el valor más alto queda abajo del embudo
df = df.sort_values("value", ascending=True).reset_index(drop=True)

# ---------------------------------------------------------------------------
# Encabezado + leyenda semáforo
# ---------------------------------------------------------------------------
st.markdown("<div class='panel-title'>Embudo de aspirantes por sede y programa (datos ficticios)</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='panel-sub'>Cada franja es un programa/sede; a la izquierda, el detalle y el total.</div>",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="legend-row">
        <span><span class="legend-dot" style="background:#E4432E"></span>&lt; 60%</span>
        <span><span class="legend-dot" style="background:#F2C94C"></span>60–80%</span>
        <span><span class="legend-dot" style="background:#27AE60"></span>&gt; 80%</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Construcción del SVG (embudo triangular ancho, colores semáforo)
# ---------------------------------------------------------------------------
def color_for_value(value: float, max_value: float) -> str:
    pct = (value / max_value) * 100 if max_value else 0
    if pct < 60:
        return "#E4432E"   # rojo de alerta
    if pct <= 80:
        return "#F2C94C"   # amarillo
    return "#27AE60"       # verde


def build_svg(rows: pd.DataFrame):
    row_height = 36
    row_gap = 0.5
    svg_h = len(rows) * row_height
    svg_w = 1140

    funnel_center_x = 840
    max_width = 540
    min_width = 10
    text_start_x = 24
    connector_anchor_x = 340

    max_value = rows["value"].max()
    values = rows["value"].tolist()

    def width_for(v):
        return min_width + (max_width - min_width) * (v / max_value)

    svg_parts = [
        """<defs>
            <filter id="bandShadow" x="-20%" y="-40%" width="140%" height="220%">
                <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#000000" flood-opacity="0.35"/>
            </filter>
        </defs>"""
    ]

    apex_w = width_for(values[0])
    base_w = width_for(values[-1])
    outline_pts = (
        f"{funnel_center_x - apex_w/2},0 "
        f"{funnel_center_x + apex_w/2},0 "
        f"{funnel_center_x + base_w/2},{svg_h} "
        f"{funnel_center_x - base_w/2},{svg_h}"
    )
    svg_parts.append(
        f'<polygon points="{outline_pts}" fill="none" stroke="#0B161E" stroke-width="3" opacity="0.9" />'
    )

    for i, row in rows.iterrows():
        y0 = i * row_height
        y1 = y0 + row_height - row_gap
        y_mid = y0 + row_height / 2

        cur_w = width_for(row["value"])
        next_w = width_for(values[i + 1]) if i < len(rows) - 1 else cur_w

        x1_left = funnel_center_x - cur_w / 2
        x1_right = funnel_center_x + cur_w / 2
        x2_left = funnel_center_x - next_w / 2
        x2_right = funnel_center_x + next_w / 2

        color = color_for_value(row["value"], max_value)

        svg_parts.append(
            f'<polygon points="{x1_left},{y0} {x1_right},{y0} {x2_right},{y1} {x2_left},{y1}" '
            f'fill="{color}" opacity="0.95" stroke="#0B161E" stroke-width="1.5" filter="url(#bandShadow)" />'
        )

        connector_band_x = (x1_left + x2_left) / 2
        svg_parts.append(
            f'<line x1="{connector_anchor_x}" y1="{y_mid}" x2="{connector_band_x}" y2="{y_mid}" '
            f'stroke="{color}" stroke-width="2" />'
        )
        svg_parts.append(f'<circle cx="{connector_anchor_x}" cy="{y_mid}" r="4" fill="{color}" />')

        label = html.escape(f"{row['sede']} • {row['programa']}")
        svg_parts.append(
            f'<text x="{text_start_x}" y="{y_mid + 4}" font-size="11.5" fill="#EAF0EE">'
            f'{label} <tspan font-weight="700" fill="{color}">— {row["value"]}</tspan></text>'
        )

        if i < len(rows) - 1:
            svg_parts.append(
                f'<line x1="{text_start_x}" y1="{y0 + row_height - 1}" x2="{connector_anchor_x - 10}" '
                f'y2="{y0 + row_height - 1}" stroke="#2A3F4E" stroke-width="0.5" opacity="0.4" />'
            )

    inner = "\n".join(svg_parts)
    svg = f'<svg viewBox="0 0 {svg_w} {svg_h}" width="100%" height="auto" xmlns="http://www.w3.org/2000/svg">{inner}</svg>'
    return svg, svg_w, svg_h


svg_markup, svg_w, svg_h = build_svg(df)

display_height = int(svg_h * 0.8) + 20
st.components.v1.html(
    f'<div style="width:100%;">{svg_markup}</div>',
    height=display_height,
    scrolling=True,
)

with st.expander("Ver datos"):
    st.dataframe(df.rename(columns={"sede": "Sede", "programa": "Programa", "value": "Valor"}), use_container_width=True)gi