from __future__ import annotations

#Calibres AWG — Área del conductor
AWG_LABELS: list[str] = [
    "18", "16", "14", "12", "10", "8", "6", "4", "3", "2", "1",
    "1/0", "2/0", "3/0", "4/0",
    "250 kcmil", "300 kcmil", "350 kcmil", "400 kcmil", "500 kcmil",
]

AWG_AREA_MM2: dict[str, float] = {
    "18":  0.823,   "16":  1.31,    "14":  2.08,    "12":  3.31,
    "10":  5.26,    "8":   8.37,    "6":  13.30,    "4":  21.15,
    "3":  26.67,    "2":  33.62,    "1":  42.41,
    "1/0": 53.49,   "2/0": 67.43,   "3/0": 85.01,   "4/0": 107.2,
    "250 kcmil": 126.7,  "300 kcmil": 152.0,  "350 kcmil": 177.3,
    "400 kcmil": 202.7,  "500 kcmil": 253.4,
}

AWG_SELECTION_ORDER: list[str] = [
    "14", "12", "10", "8", "6", "4", "2", "1",
    "1/0", "2/0", "3/0", "4/0",
]

#Áreas de conductores
INSULATION_GROUPS: list[str] = ["THW/TW", "THHN"]

INSULATED_AREA_MM2: dict[str, dict[str, float]] = {
    "THW/TW": {
        "18":  4.52,   "16":  6.13,   "14":  8.97,   "12": 11.68,
        "10": 16.77,   "8":  23.61,   "6":  37.94,   "4":  53.16,
        "3":  62.77,   "2":  74.71,   "1":  98.97,
        "1/0": 117.7,  "2/0": 140.1,  "3/0": 166.6,  "4/0": 197.8,
        "250 kcmil": 253.4, "300 kcmil": 297.5, "350 kcmil": 339.2,
        "400 kcmil": 383.6, "500 kcmil": 468.0,
    },
    "THHN": {
        "18":  3.68,   "16":  4.90,   "14":  7.16,   "12":  8.58,
        "10": 13.61,   "8":  19.48,   "6":  26.97,   "4":  41.68,
        "3":  50.97,   "2":  62.77,   "1":  81.87,
        "1/0":  98.97, "2/0": 119.7,  "3/0": 143.4,  "4/0": 171.6,
        "250 kcmil": 211.1, "300 kcmil": 248.6, "350 kcmil": 283.4,
        "400 kcmil": 320.9, "500 kcmil": 399.7,
    },
}

#Tubería Conduit 
CONDUIT_LABELS: list[str] = [
    '1/2"', '3/4"', '1"', '1 1/4"', '1 1/2"', '2"', '2 1/2"', '3"',
]

CONDUIT_PVC: dict[str, float] = {
    '1/2"':    196.0,
    '3/4"':    343.0,
    '1"':      556.0,
    '1 1/4"':  968.0,
    '1 1/2"': 1314.0,
    '2"':     2165.0,
    '2 1/2"': 3088.0,
    '3"':     4764.0,
}

#Factores de relleno 
FILL_FACTORS: dict[str, float] = {
    "1":  0.55,  
    "2":  0.30, 
    "3+": 0.40, 
}

def get_fill_factor(num_conductors: int) -> float:
    """Retorna el factor de relleno según la cantidad total de conductores."""
    if num_conductors == 1:
        return FILL_FACTORS["1"]
    if num_conductors == 2:
        return FILL_FACTORS["2"]
    return FILL_FACTORS["3+"]

#Resistividad de materiales 
RESISTIVITY: dict[str, float] = {
    "Cobre":    0.0175, 
    "Aluminio": 0.0282, 
}

#Ampacidad 
AMPACITY_COPPER: dict[str, dict[int, int]] = {
    "14":         {60: 15,   75: 20,   90: 25},
    "12":         {60: 20,   75: 25,   90: 30},
    "10":         {60: 30,   75: 35,   90: 40},
    "8":          {60: 40,   75: 50,   90: 55},
    "6":          {60: 55,   75: 65,   90: 75},
    "4":          {60: 70,   75: 85,   90: 95},
    "3":          {60: 85,   75: 100,  90: 115},
    "2":          {60: 95,   75: 115,  90: 130},
    "1":          {60: 110,  75: 130,  90: 145},
    "1/0":        {60: 125,  75: 150,  90: 170},
    "2/0":        {60: 145,  75: 175,  90: 195},
    "3/0":        {60: 165,  75: 200,  90: 225},
    "4/0":        {60: 195,  75: 230,  90: 260},
    "250 kcmil":  {60: 215,  75: 255,  90: 290},
    "300 kcmil":  {60: 240,  75: 285,  90: 320},
    "350 kcmil":  {60: 260,  75: 310,  90: 350},
    "400 kcmil":  {60: 280,  75: 335,  90: 380},
    "500 kcmil":  {60: 320,  75: 380,  90: 430},
}

#Límites de caída de tensión
VOLTAGE_DROP_LIMITS: dict[str, float] = {
    "derivado": 0.03,  
    "total":    0.05, 
}

#Tipos de cable
CABLE_TYPES: dict[str, dict] = {
    "TW": {
        "max_temp_dry":  60,
        "max_temp_wet":  60,
        "environments":  ["seco", "húmedo", "mojado"],
        "low_smoke":     False,
        "area_group":    "THW/TW",
        "description":   "Termoplástico resistente a la humedad, 60 °C",
    },
    "THW": {
        "max_temp_dry":  75,
        "max_temp_wet":  75,
        "environments":  ["seco", "húmedo", "mojado"],
        "low_smoke":     False,
        "area_group":    "THW/TW",
        "description":   "Termoplástico resistente al calor y humedad, 75 °C",
    },
    "THW-LS": {
        "max_temp_dry":  75,
        "max_temp_wet":  75,
        "environments":  ["seco", "húmedo", "mojado"],
        "low_smoke":     True,
        "area_group":    "THW/TW",
        "description":   "THW con baja emisión de humos y gases ácidos (-LS)",
    },
    "THWN": {
        "max_temp_dry":  75,
        "max_temp_wet":  75,
        "environments":  ["seco", "húmedo", "mojado"],
        "low_smoke":     False,
        "area_group":    "THHN",
        "description":   "Termoplástico con cubierta de nylon, resistente al agua, 75 °C",
    },
    "THHW": {
        "max_temp_dry":  90,
        "max_temp_wet":  75,
        "environments":  ["seco", "húmedo", "mojado"],
        "low_smoke":     False,
        "area_group":    "THW/TW",
        "description":   "Termoplástico resistente al calor y humedad (90 °C seco / 75 °C mojado)",
    },
    "THHW-LS": {
        "max_temp_dry":  90,
        "max_temp_wet":  75,
        "environments":  ["seco", "húmedo", "mojado"],
        "low_smoke":     True,
        "area_group":    "THW/TW",
        "description":   "THHW con baja emisión de humos y gases ácidos (-LS)",
    },
    "THHN": {
        "max_temp_dry":  90,
        "max_temp_wet":  None,
        "environments":  ["seco", "húmedo"],
        "low_smoke":     False,
        "area_group":    "THHN",
        "description":   "Termoplástico con nylon, alta temperatura (90 °C, solo seco/húmedo)",
    },
    "XHHW": {
        "max_temp_dry":  90,
        "max_temp_wet":  75,
        "environments":  ["seco", "húmedo", "mojado"],
        "low_smoke":     False,
        "area_group":    "THHN",
        "description":   "Polietileno de cadena cruzada (90 °C seco / 75 °C mojado)",
    },
    "RHW": {
        "max_temp_dry":  75,
        "max_temp_wet":  75,
        "environments":  ["seco", "húmedo", "mojado"],
        "low_smoke":     False,
        "area_group":    "THW/TW",
        "description":   "Hule termoestable resistente al calor y humedad, 75 °C",
    },
}

# 9. Ejemplos predeterminados del curso
EXAMPLES: dict[str, dict] = {
    "ohm_watt": {
        "title": "Foco incandescente de 100 W",
        "description": (
            "Un foco de 100 W conectado a 120 V. "
            "Calcular la corriente y la resistencia."
        ),
        "params": {"mode": "P y V", "P": 100.0, "V": 120.0},
    },
    "series": {
        "title": "Circuito serie con 3 resistencias",
        "description": (
            "Tres resistencias de 10 Ω, 20 Ω y 30 Ω conectadas en serie "
            "a una fuente de 120 V."
        ),
        "params": {"resistances": [10.0, 20.0, 30.0], "voltage": 120.0},
    },
    "energy": {
        "title": "Aire acondicionado encendido 8 horas",
        "description": (
            "Un aire acondicionado de 1500 W encendido durante 8 horas al día. "
            "Calcular el consumo diario en kWh."
        ),
        "params": {"power": 1500.0, "hours": 8.0},
    },
    "voltage_drop": {
        "title": "Circuito derivado de 30 m",
        "description": (
            "Un circuito monofásico a 127 V con cable de cobre calibre 10 AWG, "
            "30 m de longitud y carga de 20 A. Verificar la caída de tensión."
        ),
        "params": {
            "length": 30.0, "current": 20.0,
            "material": "Cobre", "awg": "10",
            "system_voltage": 127.0, "circuit_type": "derivado",
        },
    },
    "voltage_drop_inv": {
        "title": "Selección de calibre para 15 A a 50 m",
        "description": (
            "Un circuito derivado monofásico a 127 V con 15 A de carga "
            "y 50 m de recorrido en cobre. Encontrar el calibre mínimo."
        ),
        "params": {
            "length": 50.0, "current": 15.0,
            "material": "Cobre", "system_voltage": 127.0,
            "max_drop_pct": 3.0,
        },
    },
    "conduit": {
        "title": "Tubería para 3 conductores 10 AWG THHN",
        "description": (
            "Seleccionar tubería Conduit PVC para 3 conductores "
            "calibre 10 AWG con aislamiento THHN."
        ),
        "params": {
            "conductors": [
                {"qty": 3, "awg": "10", "insulation": "THHN"},
            ],
        },
    },
    "insulation": {
        "title": "Cable para cuarto de máquinas húmedo",
        "description": (
            "Seleccionar tipo de cable para un cuarto de máquinas "
            "con ambiente húmedo y temperatura máxima de 75 °C."
        ),
        "params": {
            "environment": "húmedo",
            "min_temp": 75,
            "low_smoke": False,
        },
    },
}

