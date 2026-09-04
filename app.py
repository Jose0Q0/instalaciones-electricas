from __future__ import annotations

import math
from importlib import import_module

try:
    go = import_module("plotly.graph_objects")
except ModuleNotFoundError:
    go = None

try:
    st = import_module("streamlit")
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Streamlit no esta instalado. Ejecuta: pip install streamlit"
    ) from exc

from tablas import (
    AMPACITY_COPPER,
    AWG_AREA_MM2,
    AWG_LABELS,
    AWG_SELECTION_ORDER,
    CABLE_TYPES,
    CONDUIT_PVC,
    EXAMPLES,
    FILL_FACTORS,
    INSULATED_AREA_MM2,
    INSULATION_GROUPS,
    RESISTIVITY,
    VOLTAGE_DROP_LIMITS,
)
from calculos import (
    OHM_MODES,
    calc_conduit_fill,
    calc_energy,
    calc_min_conductor,
    calc_ohm_watt,
    calc_series_circuit,
    calc_voltage_drop,
    recommend_insulation,
)

st.set_page_config(
    page_title="Calculadora Electrica ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --accent: #D4A017;
    --accent-soft: rgba(212,160,23,0.12);
    --accent-border: rgba(212,160,23,0.25);
    --surface: #0E1117;
    --surface-raised: #161B22;
    --surface-overlay: #1C2333;
    --text-primary: #E6EDF3;
    --text-muted: #8B949E;
    --pass-bg: rgba(35,134,54,0.15);
    --pass-border: rgba(35,134,54,0.4);
    --fail-bg: rgba(218,54,51,0.12);
    --fail-border: rgba(218,54,51,0.4);
    --info-bg: rgba(56,132,244,0.10);
    --info-border: rgba(56,132,244,0.35);
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

section[data-testid="stSidebar"] {
    background: var(--surface-raised);
    border-right: 1px solid rgba(212,160,23,0.08);
}

section[data-testid="stSidebar"] [data-testid="stMarkdown"] p {
    font-size: 0.88rem;
}

.brand-header {
    padding: 1.5rem 0 1.8rem 0;
    text-align: center;
    border-bottom: 1px solid rgba(212,160,23,0.10);
    margin-bottom: 1.2rem;
}
.brand-header h1 {
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
    background: linear-gradient(135deg, #D4A017, #F0C850);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.brand-header .sub {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
}

div[data-testid="stMetric"] {
    background: var(--surface-overlay);
    border: 1px solid var(--accent-border);
    border-radius: 10px;
    padding: 14px 18px;
    transition: border-color 0.2s;
}
div[data-testid="stMetric"]:hover {
    border-color: var(--accent);
}
div[data-testid="stMetric"] label {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-muted) !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}

details[data-testid="stExpander"] {
    background: var(--surface-raised);
    border: 1px solid rgba(212,160,23,0.10);
    border-radius: 8px;
    margin-bottom: 6px;
}
details[data-testid="stExpander"] summary {
    font-weight: 600;
    font-size: 0.88rem;
}

div[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.3px;
}

button[kind="primary"] {
    font-weight: 700 !important;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    font-size: 0.82rem !important;
}

button[kind="secondary"] {
    font-size: 0.78rem !important;
    opacity: 0.7;
}
button[kind="secondary"]:hover {
    opacity: 1;
}

.status-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 6px 0 12px 0;
    width: 100%;
}
.status-pass {
    background: var(--pass-bg);
    border-left: 3px solid var(--pass-border);
    color: #3FB950;
}
.status-fail {
    background: var(--fail-bg);
    border-left: 3px solid var(--fail-border);
    color: #F85149;
}
.status-info {
    background: var(--info-bg);
    border-left: 3px solid var(--info-border);
    color: #58A6FF;
}

.cable-card {
    background: var(--surface-overlay);
    border: 1px solid rgba(212,160,23,0.12);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.cable-card h4 {
    color: var(--accent);
    margin: 0 0 6px 0;
    font-size: 1rem;
}
.cable-card p {
    margin: 2px 0;
    font-size: 0.85rem;
    color: var(--text-muted);
}
.cable-card .tag {
    display: inline-block;
    background: var(--accent-soft);
    border: 1px solid var(--accent-border);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--accent);
    margin-right: 4px;
    margin-top: 6px;
}

.sidebar-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    padding: 0.5rem 0 0.3rem 0;
}

.footer {
    text-align: center;
    opacity: 0.3;
    font-size: 0.78rem;
    padding: 2rem 0 1rem 0;
    letter-spacing: 0.5px;
}

div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stCheckbox"] label {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 0.8rem 0 0.4rem 0;
}
</style>
""", unsafe_allow_html=True)


def render_steps(result: dict) -> None:
    for i, step in enumerate(result["steps"]):
        expanded = i == len(result["steps"]) - 1
        with st.expander(f"Paso {i+1}: {step['title']}", expanded=expanded):
            for latex_line in step.get("latex", []):
                st.latex(latex_line)
            if step.get("explanation"):
                st.markdown(step["explanation"])


def render_diagnosis(result: dict) -> None:
    diag = result["diagnosis"]
    css_map = {"pass": "status-pass", "fail": "status-fail"}
    css_class = css_map.get(diag["status"], "status-info")
    st.markdown(
        f'<div class="status-badge {css_class}">{diag["message"]}</div>',
        unsafe_allow_html=True,
    )


def limpiar_todo():
    st.session_state.clear()


st.markdown("""
<div class="brand-header">
    <h1>Calculadora de Instalaciones Electricas</h1>
    <div class="sub">UdeO</div>
</div>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4 = st.tabs([
    "Ohm / Watt",
    "Caida de Tension",
    "Tuberia Conduit",
    "Aislamiento",
])

with tab1:
    sub1 = st.radio(
        "Tipo de calculo",
        ["Ley de Ohm / Watt", "Circuito Serie", "Consumo Energetico"],
        horizontal=True, key="sub1",
    )

    if sub1 == "Ley de Ohm / Watt":
        c1, c2 = st.columns([1, 2])
        with c1:
            mode = st.selectbox("Variables conocidas", OHM_MODES, key="ohm_mode")
            st.button("Limpiar", key="clear_ohm", on_click=limpiar_todo)

        with c2:
            if mode == "V e I":
                v1 = st.number_input("V (Voltaje)", value=st.session_state.get("ohm_v1", 120.0),
                                     step=0.1, format="%.2f", key="ohm_vi_v")
                v2 = st.number_input("I (Corriente, A)", value=st.session_state.get("ohm_v2", 2.0),
                                     step=0.1, format="%.4f", key="ohm_vi_i")
                params = {"V": v1, "I": v2}
            elif mode == "V y R":
                v1 = st.number_input("V (Voltaje)", value=120.0, step=0.1, format="%.2f", key="ohm_vr_v")
                v2 = st.number_input("R (Resistencia)", value=60.0, step=0.1, format="%.4f", key="ohm_vr_r")
                params = {"V": v1, "R": v2}
            elif mode == "I y R":
                v1 = st.number_input("I (Corriente, A)", value=2.0, step=0.1, format="%.2f", key="ohm_ir_i")
                v2 = st.number_input("R (Resistencia)", value=60.0, step=0.1, format="%.2f", key="ohm_ir_r")
                params = {"I": v1, "R": v2}
            elif mode == "P y V":
                v1 = st.number_input("P (Potencia, W)", value=st.session_state.get("ohm_v2", 100.0),
                                     step=1.0, format="%.2f", key="ohm_pv_p")
                v2 = st.number_input("V (Voltaje)", value=st.session_state.get("ohm_v1", 120.0),
                                     step=0.1, format="%.2f", key="ohm_pv_v")
                params = {"P": v1, "V": v2}
            else:
                v1 = st.number_input("P (Potencia, W)", value=100.0, step=1.0, format="%.2f", key="ohm_pi_p")
                v2 = st.number_input("I (Corriente, A)", value=2.0, step=0.1, format="%.2f", key="ohm_pi_i")
                params = {"P": v1, "I": v2}

        if st.button("CALCULAR", key="calc_ohm", type="primary"):
            result = calc_ohm_watt(mode, **params)
            st.session_state["ohm_result"] = result

        if "ohm_result" in st.session_state:
            r = st.session_state["ohm_result"]
            render_diagnosis(r)
            cols = st.columns(4)
            for i, (k, unit) in enumerate([("V", "V"), ("I", "A"), ("R", "Ohm"), ("P", "W")]):
                with cols[i]:
                    st.metric(k, f"{r['results'][k]:.2f} {unit}")
            render_steps(r)

    elif sub1 == "Circuito Serie":
        st.button("Limpiar", key="clear_series", on_click=limpiar_todo)

        voltage = st.number_input("V fuente (V)", value=st.session_state.get("series_v", 120.0),
                                  step=0.1, format="%.2f", key="series_voltage")
        n_res = st.number_input("Numero de resistencias", value=st.session_state.get("series_n", 3),
                                min_value=2, max_value=10, step=1, key="series_n_input")

        resistances = []
        cols = st.columns(min(int(n_res), 5))
        for i in range(int(n_res)):
            with cols[i % len(cols)]:
                r_val = st.number_input(
                    f"R{i+1}", value=st.session_state.get(f"series_r{i}", 10.0),
                    min_value=0.001, step=1.0, format="%.2f", key=f"res_{i}",
                )
                resistances.append(r_val)

        if st.button("CALCULAR", key="calc_series", type="primary"):
            result = calc_series_circuit(resistances, voltage)
            st.session_state["series_result"] = result

        if "series_result" in st.session_state:
            r = st.session_state["series_result"]
            render_diagnosis(r)
            c1, c2 = st.columns(2)
            with c1:
                st.metric("R total", f"{r['results']['R_total']:.2f} Ohm")
            with c2:
                st.metric("I (constante)", f"{r['results']['I']:.2f} A")

            st.markdown('<div class="section-label">Caidas de tension por resistencia</div>', unsafe_allow_html=True)
            for i, d in enumerate(r["results"]["drops"]):
                pct = (d / voltage) * 100 if voltage else 0
                st.markdown(f"- R{i+1} = {resistances[i]} Ohm &rarr; V{i+1} = **{d:.2f} V** ({pct:.1f}%)")
            render_steps(r)

    else:
        st.button("Limpiar", key="clear_energy", on_click=limpiar_todo)

        c1, c2 = st.columns(2)
        with c1:
            power = st.number_input("P (Potencia, W)", value=st.session_state.get("energy_p", 1500.0),
                                    step=10.0, format="%.2f", key="energy_power")
        with c2:
            hours = st.number_input("t (Tiempo, horas)", value=st.session_state.get("energy_h", 8.0),
                                    step=0.5, format="%.2f", key="energy_hours")

        if st.button("CALCULAR", key="calc_energy", type="primary"):
            result = calc_energy(power, hours)
            st.session_state["energy_result"] = result

        if "energy_result" in st.session_state:
            r = st.session_state["energy_result"]
            render_diagnosis(r)
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Consumo (Wh)", f"{r['results']['Wh']:.2f}")
            with c2:
                st.metric("Consumo (kWh)", f"{r['results']['kWh']:.2f}")
            render_steps(r)

with tab2:
    sub2 = st.radio(
        "Modo de calculo",
        ["Calcular dV (directo)", "Seleccionar calibre (inverso)"],
        horizontal=True, key="sub2",
    )

    if sub2 == "Calcular dV (directo)":
        st.button("Limpiar", key="clear_vd", on_click=limpiar_todo)

        c1, c2, c3 = st.columns(3)
        with c1:
            vd_length = st.number_input("L (Longitud, m)", value=st.session_state.get("vd_length", 30.0),
                                        min_value=0.1, step=1.0, format="%.2f", key="vd_l")
            vd_current = st.number_input("I (Corriente, A)", value=st.session_state.get("vd_current", 20.0),
                                         min_value=0.01, step=0.5, format="%.2f", key="vd_i")
        with c2:
            vd_material = st.selectbox("Material", list(RESISTIVITY.keys()),
                                       index=list(RESISTIVITY.keys()).index(
                                           st.session_state.get("vd_material", "Cobre")),
                                       key="vd_mat")
            vd_awg = st.selectbox("Calibre AWG", AWG_SELECTION_ORDER,
                                  index=AWG_SELECTION_ORDER.index(
                                      st.session_state.get("vd_awg", "10")),
                                  key="vd_awg_sel")
        with c3:
            vd_voltage = st.number_input("V sistema (V)", value=st.session_state.get("vd_system_voltage", 127.0),
                                         min_value=1.0, step=1.0, format="%.1f", key="vd_vsys")
            vd_ctype = st.selectbox("Tipo de circuito",
                                    list(VOLTAGE_DROP_LIMITS.keys()),
                                    index=list(VOLTAGE_DROP_LIMITS.keys()).index(
                                        st.session_state.get("vd_circuit_type", "derivado")),
                                    key="vd_ct")

        if st.button("CALCULAR", key="calc_vd", type="primary"):
            result = calc_voltage_drop(vd_length, vd_current, vd_material,
                                       vd_awg, vd_voltage, vd_ctype)
            st.session_state["vd_result"] = result

        if "vd_result" in st.session_state:
            r = st.session_state["vd_result"]
            render_diagnosis(r)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("dV", f"{r['results']['delta_v']:.2f} V")
            with c2:
                st.metric("% dV", f"{r['results']['delta_v_pct']:.2f} %")
            with c3:
                limit = r["results"]["limit_pct"]
                st.metric("Limite normativo", f"{limit:.0f} %")
            render_steps(r)

    else:
        st.button("Limpiar", key="clear_vdi", on_click=limpiar_todo)

        c1, c2 = st.columns(2)
        with c1:
            vdi_length = st.number_input("L (Longitud, m)",
                                         value=st.session_state.get("vdi_length", 50.0),
                                         min_value=0.1, step=1.0, format="%.2f", key="vdi_l")
            vdi_current = st.number_input("I (Corriente, A)",
                                          value=st.session_state.get("vdi_current", 15.0),
                                          min_value=0.01, step=0.5, format="%.2f", key="vdi_i")
            vdi_material = st.selectbox("Material", list(RESISTIVITY.keys()),
                                        index=list(RESISTIVITY.keys()).index(
                                            st.session_state.get("vdi_material", "Cobre")),
                                        key="vdi_mat")
        with c2:
            vdi_voltage = st.number_input("V sistema (V)",
                                          value=st.session_state.get("vdi_system_voltage", 127.0),
                                          min_value=1.0, step=1.0, format="%.1f", key="vdi_vsys")
            vdi_drop = st.number_input("% dV maximo permitido",
                                       value=st.session_state.get("vdi_max_drop_pct", 3.0),
                                       min_value=0.1, max_value=10.0, step=0.5,
                                       format="%.1f", key="vdi_drop")

        if st.button("CALCULAR", key="calc_vdi", type="primary"):
            result = calc_min_conductor(vdi_length, vdi_current, vdi_material,
                                        vdi_voltage, vdi_drop)
            st.session_state["vdi_result"] = result

        if "vdi_result" in st.session_state:
            r = st.session_state["vdi_result"]
            render_diagnosis(r)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Area minima", f"{r['results']['a_min']:.2f} mm2")
            with c2:
                st.metric("Calibre recomendado", f"{r['results']['recommended_awg']} AWG")
            with c3:
                st.metric("% dV real", f"{r['results']['dv_actual_pct']:.2f} %")
            render_steps(r)

with tab3:
    st.button("Limpiar", key="clear_conduit", on_click=limpiar_todo)

    if "conduit_rows" not in st.session_state:
        st.session_state["conduit_rows"] = [
            {"qty": 3, "awg": "12", "insulation": "THHN"},
        ]

    st.markdown('<div class="section-label">Conductores en la tuberia</div>', unsafe_allow_html=True)

    bc1, bc2, _ = st.columns([1, 1, 3])
    with bc1:
        if st.button("Agregar fila", key="add_row"):
            st.session_state["conduit_rows"].append(
                {"qty": 1, "awg": "12", "insulation": "THHN"}
            )
            st.rerun()
    with bc2:
        if len(st.session_state["conduit_rows"]) > 1:
            if st.button("Quitar ultima", key="rm_row"):
                st.session_state["conduit_rows"].pop()
                st.rerun()

    insulation_options = ["THHN", "THW/TW", "THWN", "XHHW"]
    awg_options = list(AWG_AREA_MM2.keys())

    conductors_input: list[dict] = []
    for i, row in enumerate(st.session_state["conduit_rows"]):
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            qty = st.number_input(
                f"Cantidad (grupo {i+1})", value=row["qty"],
                min_value=1, max_value=50, step=1, key=f"cqty_{i}",
            )
        with rc2:
            awg_idx = awg_options.index(row["awg"]) if row["awg"] in awg_options else 3
            awg = st.selectbox(
                f"Calibre AWG (grupo {i+1})", awg_options,
                index=awg_idx, key=f"cawg_{i}",
            )
        with rc3:
            ins_idx = insulation_options.index(row["insulation"]) if row["insulation"] in insulation_options else 0
            ins = st.selectbox(
                f"Aislamiento (grupo {i+1})", insulation_options,
                index=ins_idx, key=f"cins_{i}",
            )
        conductors_input.append({"qty": qty, "awg": awg, "insulation": ins})
        st.session_state["conduit_rows"][i] = {"qty": qty, "awg": awg, "insulation": ins}

    if st.button("CALCULAR", key="calc_conduit", type="primary"):
        result = calc_conduit_fill(conductors_input)
        st.session_state["conduit_result"] = result

    if "conduit_result" in st.session_state:
        r = st.session_state["conduit_result"]
        render_diagnosis(r)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Area conductores", f"{r['results']['total_area']:.2f} mm2")
        with c2:
            st.metric("Area tubo minima", f"{r['results']['a_tube_min']:.2f} mm2")
        with c3:
            sel = r["results"]["selected_conduit"] or "N/A"
            st.metric("Tuberia", sel)
        with c4:
            fp = r["results"].get("fill_actual_pct")
            st.metric("Relleno real", f"{fp:.1f} %" if fp else "N/A")
        render_steps(r)

with tab4:
    st.button("Limpiar", key="clear_ins", on_click=limpiar_todo)

    c1, c2, c3 = st.columns(3)
    environments = ["seco", "humedo", "mojado"]
    with c1:
        env = st.selectbox("Ambiente / Entorno", environments,
                           index=environments.index(
                               st.session_state.get("ins_env", "seco")),
                           key="ins_env_sel")
    with c2:
        temps = [60, 75, 90]
        temp = st.selectbox("Temperatura minima requerida", temps,
                            index=temps.index(
                                st.session_state.get("ins_temp", 75)),
                            key="ins_temp_sel")
    with c3:
        low_smoke = st.checkbox("Requiere baja emision de humos (-LS)",
                                value=st.session_state.get("ins_ls", False),
                                key="ins_ls_check")

    if st.button("EVALUAR", key="calc_ins", type="primary"):
        result = recommend_insulation(env, temp, low_smoke)
        st.session_state["ins_result"] = result

    if "ins_result" in st.session_state:
        r = st.session_state["ins_result"]
        render_diagnosis(r)

        recommended = r["results"]["recommended"]
        rejected = r["results"]["rejected"]

        if recommended:
            st.markdown('<div class="section-label">Cables recomendados</div>', unsafe_allow_html=True)
            for rec in recommended:
                props = rec["props"]
                temp_str = f"{props['max_temp_dry']}C"
                if props["max_temp_wet"] and props["max_temp_wet"] != props["max_temp_dry"]:
                    temp_str += f" seco / {props['max_temp_wet']}C mojado"
                envs = ", ".join(props["environments"])
                ls_tag = '<span class="tag">BAJA EMISION</span>' if props["low_smoke"] else ""
                st.markdown(f"""
                <div class="cable-card">
                    <h4>{rec['name']}</h4>
                    <p><strong>{props['description']}</strong></p>
                    <p>Temperatura: {temp_str}</p>
                    <p>Ambientes: {envs}</p>
                    {ls_tag}
                </div>
                """, unsafe_allow_html=True)

        if rejected:
            with st.expander(f"Cables descartados ({len(rejected)})"):
                for rej in rejected:
                    reason = rej["reasons"][0]
                    st.markdown(f"- **{rej['name']}**: {reason}")

        render_steps(r)

with st.sidebar:
    st.markdown('<div class="sidebar-title">Tablas de referencia</div>', unsafe_allow_html=True)
    st.markdown("---")

    with st.expander("AWG / mm2 / Ampacidad"):
        for awg in AWG_SELECTION_ORDER:
            area = AWG_AREA_MM2[awg]
            amp_75 = AMPACITY_COPPER.get(awg, {}).get(75, "-")
            st.markdown(f"**{awg}** AWG = {area} mm2 ({amp_75} A @ 75C)")

    with st.expander("Tuberia Conduit PVC"):
        for label, area in CONDUIT_PVC.items():
            d = 2 * math.sqrt(area / math.pi)
            st.markdown(f"**{label}**: {area} mm2 (d = {d:.1f} mm)")

    with st.expander("Resistividades"):
        for mat, rho in RESISTIVITY.items():
            st.markdown(f"**{mat}**: p = {rho} Ohm mm2/m")

    with st.expander("Factores de relleno NOM"):
        for k, v in FILL_FACTORS.items():
            label = f"{k} conductor(es)" if k != "3+" else "3 o mas conductores"
            st.markdown(f"**{label}**: {v*100:.0f}%")


st.markdown('<div class="footer">Hecho por: José Mario García Caxaj</div>', unsafe_allow_html=True)
