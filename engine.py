"""
engine.py — Motor de cálculos para instalaciones eléctricas de baja tensión.

Funciones puras que reciben parámetros numéricos y retornan diccionarios con:
  - "steps":     lista de pasos con LaTeX y explicaciones
  - "results":   diccionario de resultados numéricos
  - "diagnosis": estado ("pass" / "fail" / "info") y mensaje

La lógica está completamente separada de la interfaz (app.py).
"""

from __future__ import annotations

import math
from typing import Any

from app_config import (
    AWG_AREA_MM2,
    AWG_SELECTION_ORDER,
    CABLE_TYPES,
    CONDUIT_LABELS,
    CONDUIT_PVC,
    INSULATED_AREA_MM2,
    RESISTIVITY,
    VOLTAGE_DROP_LIMITS,
    get_fill_factor,
)


# ──────────────────────────── Helpers ────────────────────────────


def _fmt(x: float, d: int = 4) -> str:
    """Formatea un número: enteros sin decimales, flotantes con *d* dígitos."""
    if isinstance(x, int) or (isinstance(x, float) and x == int(x) and abs(x) < 1e12):
        return str(int(x))
    return f"{x:.{d}f}"


def _fmu(x: float, unit: str, d: int = 4) -> str:
    r"""Formatea número con unidad LaTeX: ``120\ \text{V}``."""
    return rf"{_fmt(x, d)}\ \text{{{unit}}}"


def _step(title: str, latex: list[str], explanation: str = "") -> dict:
    """Atajo para crear un paso del procedimiento."""
    return {"title": title, "latex": latex, "explanation": explanation}


# ══════════════════════════════════════════════════════════════════
# MÓDULO 1 — Ley de Ohm, Ley de Watt y Circuitos Básicos
# ══════════════════════════════════════════════════════════════════


OHM_MODES = [
    "V e I",     # → R, P
    "V y R",     # → I, P
    "I y R",     # → V, P
    "P y V",     # → I, R
    "P e I",     # → V, R
]


def calc_ohm_watt(mode: str, **kw) -> dict:
    """Cálculo de Ley de Ohm / Ley de Watt según variables conocidas."""

    steps: list[dict] = []
    results: dict[str, float] = {}

    if mode == "V e I":
        V, I = kw["V"], kw["I"]
        R = V / I
        P = V * I
        results = {"V": V, "I": I, "R": R, "P": P}

        steps.append(_step("Fórmulas Aplicadas", [
            r"R = \frac{V}{I}", r"P = V \cdot I",
        ]))
        steps.append(_step("Sustitución Numérica", [
            rf"R = \frac{{{_fmu(V, 'V')}}}{{{_fmu(I, 'A')}}}",
            rf"P = {_fmu(V, 'V')} \times {_fmu(I, 'A')}",
        ]))
        steps.append(_step("Resultado", [
            rf"\boxed{{R = {_fmu(R, 'Ω')}}}",
            rf"\boxed{{P = {_fmu(P, 'W')}}}",
        ]))

    elif mode == "V y R":
        V, R = kw["V"], kw["R"]
        I = V / R
        P = V ** 2 / R
        results = {"V": V, "I": I, "R": R, "P": P}

        steps.append(_step("Fórmulas Aplicadas", [
            r"I = \frac{V}{R}", r"P = \frac{V^2}{R}",
        ]))
        steps.append(_step("Sustitución Numérica", [
            rf"I = \frac{{{_fmu(V, 'V')}}}{{{_fmu(R, 'Ω')}}}",
            rf"P = \frac{{({_fmt(V)})^2}}{{{_fmu(R, 'Ω')}}} = \frac{{{_fmu(V**2, 'V²')}}}{{{_fmu(R, 'Ω')}}}",
        ]))
        steps.append(_step("Resultado", [
            rf"\boxed{{I = {_fmu(I, 'A')}}}",
            rf"\boxed{{P = {_fmu(P, 'W')}}}",
        ]))

    elif mode == "I y R":
        I, R = kw["I"], kw["R"]
        V = I * R
        P = I ** 2 * R
        results = {"V": V, "I": I, "R": R, "P": P}

        steps.append(_step("Fórmulas Aplicadas", [
            r"V = I \cdot R", r"P = I^2 \cdot R",
        ]))
        steps.append(_step("Sustitución Numérica", [
            rf"V = {_fmu(I, 'A')} \times {_fmu(R, 'Ω')}",
            rf"P = ({_fmt(I)})^2 \times {_fmu(R, 'Ω')} = {_fmu(I**2, 'A²')} \times {_fmu(R, 'Ω')}",
        ]))
        steps.append(_step("Resultado", [
            rf"\boxed{{V = {_fmu(V, 'V')}}}",
            rf"\boxed{{P = {_fmu(P, 'W')}}}",
        ]))

    elif mode == "P y V":
        P, V = kw["P"], kw["V"]
        I = P / V
        R = V ** 2 / P
        results = {"V": V, "I": I, "R": R, "P": P}

        steps.append(_step("Fórmulas Aplicadas", [
            r"I = \frac{P}{V}", r"R = \frac{V^2}{P}",
        ]))
        steps.append(_step("Sustitución Numérica", [
            rf"I = \frac{{{_fmu(P, 'W')}}}{{{_fmu(V, 'V')}}}",
            rf"R = \frac{{({_fmt(V)})^2}}{{{_fmu(P, 'W')}}} = \frac{{{_fmu(V**2, 'V²')}}}{{{_fmu(P, 'W')}}}",
        ]))
        steps.append(_step("Resultado", [
            rf"\boxed{{I = {_fmu(I, 'A')}}}",
            rf"\boxed{{R = {_fmu(R, 'Ω')}}}",
        ]))

    elif mode == "P e I":
        P, I = kw["P"], kw["I"]
        V = P / I
        R = P / I ** 2
        results = {"V": V, "I": I, "R": R, "P": P}

        steps.append(_step("Fórmulas Aplicadas", [
            r"V = \frac{P}{I}", r"R = \frac{P}{I^2}",
        ]))
        steps.append(_step("Sustitución Numérica", [
            rf"V = \frac{{{_fmu(P, 'W')}}}{{{_fmu(I, 'A')}}}",
            rf"R = \frac{{{_fmu(P, 'W')}}}{{({_fmt(I)})^2}} = \frac{{{_fmu(P, 'W')}}}{{{_fmu(I**2, 'A²')}}}",
        ]))
        steps.append(_step("Resultado", [
            rf"\boxed{{V = {_fmu(V, 'V')}}}",
            rf"\boxed{{R = {_fmu(R, 'Ω')}}}",
        ]))

    # Paso 4: Diagnóstico
    steps.append(_step("Diagnóstico", [],
        f"Cálculo completado. Potencia: **{_fmt(results['P'])} W** "
        f"({_fmt(results['P'] / 1000, 2)} kW)."
    ))

    return {"steps": steps, "results": results,
            "diagnosis": {"status": "info", "message": "Cálculo completado correctamente."}}


# ── Circuito serie ──


def calc_series_circuit(resistances: list[float], voltage: float) -> dict:
    """Análisis de circuito serie: R_total, I, divisiones de tensión."""

    R_total = sum(resistances)
    I = voltage / R_total
    drops = [I * r for r in resistances]
    n = len(resistances)

    # Paso 1
    r_latex = " + ".join(rf"R_{{{i+1}}}" for i in range(n))
    r_vals = " + ".join(_fmu(r, "Ω") for r in resistances)
    s1 = _step("Fórmulas Aplicadas", [
        rf"R_{{total}} = {r_latex}",
        r"I = \frac{V}{R_{total}}",
        r"V_i = I \cdot R_i \quad (\text{división de tensión})",
    ])

    # Paso 2
    s2 = _step("Sustitución Numérica", [
        rf"R_{{total}} = {r_vals} = {_fmu(R_total, 'Ω')}",
        rf"I = \frac{{{_fmu(voltage, 'V')}}}{{{_fmu(R_total, 'Ω')}}} = {_fmu(I, 'A')}",
    ])

    # Paso 3
    drop_lines = [
        rf"V_{{{i+1}}} = {_fmu(I, 'A')} \times {_fmu(r, 'Ω')} = {_fmu(d, 'V')}"
        for i, (r, d) in enumerate(zip(resistances, drops))
    ]
    sum_check = sum(drops)
    drop_lines.append(rf"\sum V_i = {_fmu(sum_check, 'V')} \; (\text{{verificación}})")
    s3 = _step("Resultado", [
        rf"\boxed{{R_{{total}} = {_fmu(R_total, 'Ω')}}}",
        rf"\boxed{{I = {_fmu(I, 'A')}}}",
    ] + drop_lines)

    # Paso 4
    s4 = _step("Diagnóstico", [],
        f"Circuito serie con **{n} resistencias**. "
        f"La corriente constante es **{_fmt(I)} A** en todo el circuito. "
        f"La suma de caídas de tensión ({_fmt(sum_check)} V) "
        f"{'coincide' if abs(sum_check - voltage) < 0.001 else 'NO coincide'} "
        f"con el voltaje de la fuente ({_fmt(voltage)} V)."
    )

    results = {"R_total": R_total, "I": I, "drops": drops}
    return {"steps": [s1, s2, s3, s4], "results": results,
            "diagnosis": {"status": "pass", "message": "Ley de Kirchhoff verificada."}}


# ── Consumo energético ──


def calc_energy(power_w: float, hours: float) -> dict:
    """W = P × t en kWh."""

    wh = power_w * hours
    kwh = wh / 1000.0

    s1 = _step("Fórmulas Aplicadas", [
        r"W = P \times t",
        r"W_{kWh} = \frac{P \times t}{1000}",
    ])
    s2 = _step("Sustitución Numérica", [
        rf"W = {_fmu(power_w, 'W')} \times {_fmu(hours, 'h')}",
        rf"W = {_fmu(wh, 'Wh')}",
    ])
    s3 = _step("Resultado", [
        rf"\boxed{{W = {_fmu(kwh, 'kWh')}}}",
    ], f"Consumo total: **{_fmt(kwh)} kWh**.")
    s4 = _step("Diagnóstico", [],
        f"Equivale a un consumo diario de **{_fmt(kwh)} kWh** "
        f"({_fmt(kwh * 30, 2)} kWh/mes estimado si se usa diariamente)."
    )

    return {"steps": [s1, s2, s3, s4],
            "results": {"Wh": wh, "kWh": kwh},
            "diagnosis": {"status": "info", "message": f"Consumo: {_fmt(kwh)} kWh."}}


# ══════════════════════════════════════════════════════════════════
# MÓDULO 2 — Caída de Tensión y Selección de Calibre
# ══════════════════════════════════════════════════════════════════


def calc_voltage_drop(
    length: float, current: float, material: str,
    awg: str, system_voltage: float, circuit_type: str = "derivado",
) -> dict:
    """Caída de tensión monofásica: ΔV = 2·L·I·ρ / A."""

    rho = RESISTIVITY[material]
    area = AWG_AREA_MM2[awg]
    dv = 2 * length * current * rho / area
    dv_pct = (dv / system_voltage) * 100
    limit_pct = VOLTAGE_DROP_LIMITS[circuit_type] * 100

    # Paso 1
    s1 = _step("Fórmulas Aplicadas", [
        r"\Delta V = \frac{2 \cdot L \cdot I \cdot \rho}{A}",
        r"\%\Delta V = \frac{\Delta V}{V_{sistema}} \times 100",
    ], "Fórmula para circuitos monofásicos (ida y vuelta del conductor).")

    # Paso 2
    s2 = _step("Sustitución Numérica", [
        rf"\rho_{{\text{{{material}}}}} = {_fmu(rho, 'Ω·mm²/m')}",
        rf"A_{{{awg}\,\text{{AWG}}}} = {_fmu(area, 'mm²')}",
        rf"\Delta V = \frac{{2 \times {_fmu(length, 'm')} \times {_fmu(current, 'A')} \times {_fmt(rho)}}}{{{_fmu(area, 'mm²')}}}",
    ])

    # Paso 3
    s3 = _step("Resultado", [
        rf"\boxed{{\Delta V = {_fmu(dv, 'V')}}}",
        rf"\%\Delta V = \frac{{{_fmt(dv)}}}{{{_fmt(system_voltage)}}} \times 100 = {_fmt(dv_pct, 2)}\%",
    ])

    # Paso 4: Diagnóstico
    passes = dv_pct <= limit_pct
    if passes:
        status = "pass"
        msg = (f"✅ **Cumple con la norma.** La caída de tensión ({_fmt(dv_pct, 2)}%) "
               f"no excede el límite de {_fmt(limit_pct)}% para circuito {circuit_type}.")
    else:
        # Sugerir calibre adecuado
        suggestion = _suggest_awg(length, current, rho, system_voltage, limit_pct)
        status = "fail"
        msg = (f"❌ **Excede el límite normativo.** La caída de tensión ({_fmt(dv_pct, 2)}%) "
               f"supera el máximo de {_fmt(limit_pct)}% para circuito {circuit_type}. "
               f"**Propuesta:** Usar calibre **{suggestion}** o mayor.")

    s4 = _step("Diagnóstico y Validación Normativa", [
        rf"\%\Delta V = {_fmt(dv_pct, 2)}\% \quad \text{{vs}} \quad \text{{Límite}} = {_fmt(limit_pct)}\%",
    ], msg)

    return {"steps": [s1, s2, s3, s4],
            "results": {"delta_v": dv, "delta_v_pct": dv_pct, "limit_pct": limit_pct},
            "diagnosis": {"status": status, "message": msg}}


def calc_min_conductor(
    length: float, current: float, material: str,
    system_voltage: float, max_drop_pct: float,
) -> dict:
    """Cálculo inverso: área mínima y calibre AWG recomendado."""

    rho = RESISTIVITY[material]
    dv_allowed = system_voltage * max_drop_pct / 100.0
    a_min = 2 * length * current * rho / dv_allowed
    recommended = _suggest_awg_from_area(a_min)
    rec_area = AWG_AREA_MM2.get(recommended, a_min)

    # Verificar la caída real con el calibre recomendado
    dv_actual = 2 * length * current * rho / rec_area
    dv_actual_pct = (dv_actual / system_voltage) * 100

    s1 = _step("Fórmulas Aplicadas", [
        r"A_{min} = \frac{2 \cdot L \cdot I \cdot \rho}{\Delta V_{permitido}}",
        r"\Delta V_{permitido} = V_{sistema} \times \frac{\%\Delta V}{100}",
    ])
    s2 = _step("Sustitución Numérica", [
        rf"\Delta V_{{permitido}} = {_fmt(system_voltage)} \times \frac{{{_fmt(max_drop_pct)}}}{{100}} = {_fmu(dv_allowed, 'V')}",
        rf"A_{{min}} = \frac{{2 \times {_fmt(length)} \times {_fmt(current)} \times {_fmt(rho)}}}{{{_fmt(dv_allowed)}}}",
    ])
    s3 = _step("Resultado", [
        rf"\boxed{{A_{{min}} = {_fmu(a_min, 'mm²')}}}",
        rf"\text{{Calibre recomendado: }} \boxed{{{recommended}\ \text{{AWG}}}} \;({_fmu(rec_area, 'mm²')})",
    ], f"Se selecciona el calibre comercial inmediato superior: **{recommended} AWG** "
       f"(área = {_fmt(rec_area)} mm²).")

    s4 = _step("Diagnóstico y Validación Normativa", [
        rf"\Delta V_{{real}} = \frac{{2 \times {_fmt(length)} \times {_fmt(current)} \times {_fmt(rho)}}}{{{_fmt(rec_area)}}} = {_fmu(dv_actual, 'V')}",
        rf"\%\Delta V_{{real}} = {_fmt(dv_actual_pct, 2)}\% \leq {_fmt(max_drop_pct)}\%",
    ], f"✅ Con calibre **{recommended} AWG**, la caída real es "
       f"**{_fmt(dv_actual_pct, 2)}%** ≤ {_fmt(max_drop_pct)}%.")

    return {"steps": [s1, s2, s3, s4],
            "results": {"a_min": a_min, "recommended_awg": recommended,
                        "rec_area": rec_area, "dv_actual": dv_actual,
                        "dv_actual_pct": dv_actual_pct},
            "diagnosis": {"status": "pass",
                          "message": f"Calibre recomendado: {recommended} AWG."}}


def _suggest_awg(length, current, rho, system_voltage, limit_pct):
    """Encuentra el calibre AWG mínimo que cumple la caída de tensión."""
    dv_max = system_voltage * limit_pct / 100.0
    a_min = 2 * length * current * rho / dv_max
    return _suggest_awg_from_area(a_min)


def _suggest_awg_from_area(a_min: float) -> str:
    """Retorna el AWG con área ≥ a_min."""
    for awg in AWG_SELECTION_ORDER:
        if AWG_AREA_MM2[awg] >= a_min:
            return awg
    return "4/0"  # Máximo estándar


# ══════════════════════════════════════════════════════════════════
# MÓDULO 3 — Dimensionamiento de Tubería Conduit PVC
# ══════════════════════════════════════════════════════════════════


def calc_conduit_fill(conductors: list[dict]) -> dict:
    """Calcula el factor de relleno y selecciona tubería Conduit PVC.

    conductors: [{"qty": int, "awg": str, "insulation": str}, ...]
    """

    # Calcular área total de conductores y cantidad total
    total_qty = sum(c["qty"] for c in conductors)
    details: list[dict] = []
    total_area = 0.0

    for c in conductors:
        # Determinar grupo de aislamiento
        ins = c["insulation"]
        if ins in ("THHN", "THWN", "XHHW"):
            group = "THHN"
        else:
            group = "THW/TW"

        unit_area = INSULATED_AREA_MM2[group].get(c["awg"], 0)
        subtotal = c["qty"] * unit_area
        total_area += subtotal
        details.append({
            "qty": c["qty"], "awg": c["awg"], "insulation": ins,
            "group": group, "unit_area": unit_area, "subtotal": subtotal,
        })

    # Factor de relleno
    fr = get_fill_factor(total_qty)
    fr_pct = fr * 100

    # Área mínima del tubo
    a_tube_min = total_area / fr

    # Diámetro teórico
    d_min = 2 * math.sqrt(a_tube_min / math.pi)

    # Seleccionar tubo comercial
    selected_conduit = None
    selected_area = 0
    for label in CONDUIT_LABELS:
        area = CONDUIT_PVC[label]
        if area * fr >= total_area:
            selected_conduit = label
            selected_area = area
            break

    # ── Pasos ──
    # Paso 1
    area_lines = []
    for det in details:
        area_lines.append(
            rf"{det['qty']} \times {det['awg']}\;\text{{AWG ({det['insulation']})}}"
            rf" = {det['qty']} \times {_fmu(det['unit_area'], 'mm²')}"
            rf" = {_fmu(det['subtotal'], 'mm²')}"
        )
    s1 = _step("Fórmulas Aplicadas", [
        r"A_c = \sum (n_i \times A_{conductor,i})",
        r"A_T = \frac{A_c}{F_r}",
        r"d = 2\sqrt{\frac{A_T}{\pi}}",
    ] + area_lines)

    # Paso 2
    s2 = _step("Sustitución Numérica", [
        rf"A_c = {_fmu(total_area, 'mm²')}",
        rf"\text{{Conductores totales}} = {total_qty} \Rightarrow F_r = {_fmt(fr_pct, 0)}\%",
        rf"A_T = \frac{{{_fmt(total_area)}}}{{{_fmt(fr)}}} = {_fmu(a_tube_min, 'mm²')}",
        rf"d_{{min}} = 2\sqrt{{\frac{{{_fmt(a_tube_min)}}}{{\pi}}}} = {_fmu(d_min, 'mm')}",
    ])

    # Paso 3
    if selected_conduit:
        fill_actual = (total_area / selected_area) * 100
        s3 = _step("Resultado", [
            rf"\boxed{{\text{{Tubería: }} {selected_conduit}\;\text{{Conduit PVC}}}}",
            rf"A_{{tubo}} = {_fmu(selected_area, 'mm²')}",
            rf"\text{{Relleno real}} = \frac{{{_fmt(total_area)}}}{{{_fmt(selected_area)}}} \times 100 = {_fmt(fill_actual, 2)}\%",
        ], f"Tubería seleccionada: **{selected_conduit}** Conduit PVC "
           f"(relleno real: {_fmt(fill_actual, 1)}%, máximo permitido: {_fmt(fr_pct, 0)}%).")
    else:
        fill_actual = 100
        s3 = _step("Resultado", [],
            "⚠️ Ninguna tubería estándar satisface el requerimiento. "
            "Considere dividir los conductores en múltiples tuberías.")

    # Paso 4
    passes = selected_conduit is not None and fill_actual <= fr_pct
    if passes:
        msg = (f"✅ **Cumple con la norma.** El factor de relleno real "
               f"({_fmt(fill_actual, 1)}%) no excede el {_fmt(fr_pct, 0)}% permitido.")
        status = "pass"
    elif selected_conduit:
        msg = (f"❌ **Factor de relleno superado.** El relleno real "
               f"({_fmt(fill_actual, 1)}%) excede el {_fmt(fr_pct, 0)}% permitido. "
               f"Considere una tubería de mayor diámetro.")
        status = "fail"
    else:
        msg = "❌ **Se requieren tuberías múltiples.** La carga excede toda tubería estándar."
        status = "fail"

    s4 = _step("Diagnóstico y Validación Normativa", [], msg)

    return {
        "steps": [s1, s2, s3, s4],
        "results": {
            "total_area": total_area, "total_qty": total_qty,
            "fill_factor": fr, "a_tube_min": a_tube_min,
            "d_min": d_min, "selected_conduit": selected_conduit,
            "selected_area": selected_area,
            "fill_actual_pct": fill_actual if selected_conduit else None,
        },
        "diagnosis": {"status": status, "message": msg},
    }


# ══════════════════════════════════════════════════════════════════
# MÓDULO 4 — Asistente de Aislamiento y Entorno Ambiental
# ══════════════════════════════════════════════════════════════════


def recommend_insulation(
    environment: str,
    min_temp: int,
    low_smoke: bool = False,
) -> dict:
    """Recomienda tipos de cable según condiciones del proyecto.

    environment: "seco", "húmedo", "mojado"
    min_temp: temperatura mínima requerida en °C (60, 75, 90)
    low_smoke: si se requiere baja emisión de humos (-LS)
    """

    recommended: list[dict] = []
    rejected: list[dict] = []

    # Determinar si usamos max_temp_dry o max_temp_wet según el ambiente
    use_wet = environment == "mojado"

    for name, props in CABLE_TYPES.items():
        reasons_reject: list[str] = []
        reasons_accept: list[str] = []

        # 1. Verificar ambiente
        if environment not in props["environments"]:
            reasons_reject.append(f"No apto para ambiente {environment}")

        # 2. Verificar temperatura
        if use_wet and props["max_temp_wet"] is not None:
            effective_temp = props["max_temp_wet"]
        elif use_wet and props["max_temp_wet"] is None:
            effective_temp = 0  # No apto para mojado
            reasons_reject.append("No tiene clasificación para ambiente mojado")
        else:
            effective_temp = props["max_temp_dry"]

        if effective_temp < min_temp:
            reasons_reject.append(
                f"Temperatura máxima ({effective_temp} °C) insuficiente "
                f"(se requiere ≥ {min_temp} °C)")

        # 3. Verificar baja emisión de humos
        if low_smoke and not props["low_smoke"]:
            reasons_reject.append("No tiene clasificación -LS (baja emisión de humos)")

        if reasons_reject:
            rejected.append({"name": name, "props": props, "reasons": reasons_reject})
        else:
            reasons_accept.append(f"Ambiente {environment}: ✅")
            reasons_accept.append(f"Temperatura: {effective_temp} °C ≥ {min_temp} °C ✅")
            if low_smoke:
                reasons_accept.append("Baja emisión de humos (-LS): ✅")
            recommended.append({"name": name, "props": props, "reasons": reasons_accept})

    # ── Pasos ──
    s1 = _step("Criterios de Selección", [
        rf"\text{{Ambiente: {environment}}}",
        rf"\text{{Temperatura mínima: {min_temp}°C}}",
        rf"\text{{Baja emisión de humos: {'Sí' if low_smoke else 'No'}}}",
    ], "Se evalúa cada tipo de cable contra los requisitos del proyecto.")

    s2_lines = []
    for r in recommended:
        s2_lines.append(rf"\checkmark\; \textbf{{{r['name']}}} — {r['props']['description']}")
    for r in rejected[:3]:  # Mostrar hasta 3 rechazados
        reason = r["reasons"][0]
        s2_lines.append(rf"\times\; \text{{{r['name']}}}: {reason}")

    s2 = _step("Evaluación de Tipos de Cable", s2_lines)

    s3_lines = [rf"\textbf{{{r['name']}}}" for r in recommended]
    if s3_lines:
        s3 = _step("Resultado", [
            r"\text{Tipos de cable recomendados:}",
        ] + s3_lines,
            f"Se encontraron **{len(recommended)} tipos** de cable compatibles.")
    else:
        s3 = _step("Resultado", [],
            "⚠️ **No se encontraron cables compatibles** con todos los requisitos. "
            "Revise los criterios o considere cables especializados.")

    if recommended:
        best = recommended[0]["name"]
        msg = (f"✅ Cable recomendado: **{best}**. "
               f"Total de opciones compatibles: {len(recommended)}.")
        status = "pass"
    else:
        msg = "❌ No hay cables compatibles con todos los requisitos."
        status = "fail"

    s4 = _step("Diagnóstico", [], msg)

    return {
        "steps": [s1, s2, s3, s4],
        "results": {"recommended": recommended, "rejected": rejected},
        "diagnosis": {"status": status, "message": msg},
    }

