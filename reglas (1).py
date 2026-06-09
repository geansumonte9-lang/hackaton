def _ev_rampa(v):
    p = v.get("pendiente", 0.0)
    L = v.get("largo", 0.0)
    if p <= 0 or L <= 0:
        return None, ""
    if L <= 1.5:
        maximo = 12.0
    elif L >= 9:
        maximo = 8.0
    else:
        maximo = 12.8 - 0.5333 * L
    estado = "No cumple" if p > maximo + 1e-9 else "Cumple"
    return estado, f"Pendiente {p:g}% en {L:g} m (máximo permitido {maximo:.1f}%)."


def _ev_min(clave, minimo, unidad, etiqueta):
    def f(v):
        x = v.get(clave, 0.0)
        if x <= 0:
            return None, ""
        estado = "No cumple" if x < minimo else "Cumple"
        return estado, f"{etiqueta}: {x:g} {unidad} (mínimo {minimo:g} {unidad})."
    return f


def _ev_max(clave, maximo, unidad, etiqueta):
    def f(v):
        x = v.get(clave, 0.0)
        if x <= 0:
            return None, ""
        estado = "No cumple" if x > maximo else "Cumple"
        return estado, f"{etiqueta}: {x:g} {unidad} (máximo {maximo:g} {unidad})."
    return f


def _ev_rango(clave, lo, hi, unidad, etiqueta):
    def f(v):
        x = v.get(clave, 0.0)
        if x <= 0:
            return None, ""
        estado = "Cumple" if lo <= x <= hi else "No cumple"
        return estado, f"{etiqueta}: {x:g} {unidad} (debe estar entre {lo:g} y {hi:g} {unidad})."
    return f


REGLAS = {
    "RAMPA_PENDIENTE": {
        "campos": [
            {"clave": "pendiente", "etiqueta": "Pendiente medida", "unidad": "%"},
            {"clave": "largo", "etiqueta": "Largo del tramo", "unidad": "m"},
        ],
        "evaluar": _ev_rampa,
    },
    "PUERTA_ANCHO": {
        "campos": [{"clave": "ancho", "etiqueta": "Ancho libre", "unidad": "cm"}],
        "evaluar": _ev_min("ancho", 90, "cm", "Ancho libre de puerta"),
    },
    "RUTA_ANCHO": {
        "campos": [{"clave": "ancho", "etiqueta": "Ancho libre", "unidad": "cm"}],
        "evaluar": _ev_min("ancho", 120, "cm", "Ancho de ruta accesible"),
    },
    "RUTA_ALTURA_LIBRE": {
        "campos": [{"clave": "altura", "etiqueta": "Altura libre", "unidad": "cm"}],
        "evaluar": _ev_min("altura", 210, "cm", "Altura libre de paso"),
    },
    "RUTA_PENDIENTE_TRANSVERSAL": {
        "campos": [{"clave": "pend_t", "etiqueta": "Pendiente transversal", "unidad": "%"}],
        "evaluar": _ev_max("pend_t", 2, "%", "Pendiente transversal"),
    },
    "REBAJE_SOLERA": {
        "campos": [{"clave": "resalto", "etiqueta": "Resalto del rebaje", "unidad": "mm"}],
        "evaluar": _ev_max("resalto", 8, "mm", "Resalto de solera"),
    },
    "DESNIVEL_UMBRAL": {
        "campos": [{"clave": "resalto", "etiqueta": "Altura del resalto", "unidad": "cm"}],
        "evaluar": _ev_max("resalto", 2, "cm", "Resalto / umbral"),
    },
    "PASILLO_GIRO": {
        "campos": [{"clave": "ancho", "etiqueta": "Ancho de pasillo", "unidad": "cm"}],
        "evaluar": _ev_min("ancho", 90, "cm", "Ancho de pasillo"),
    },
    "BANO_GIRO": {
        "campos": [{"clave": "diametro", "etiqueta": "Diámetro de giro libre", "unidad": "cm"}],
        "evaluar": _ev_min("diametro", 150, "cm", "Diámetro de giro"),
    },
    "BANO_INODORO": {
        "campos": [{"clave": "altura_taza", "etiqueta": "Altura de la taza", "unidad": "cm"}],
        "evaluar": _ev_rango("altura_taza", 46, 48, "cm", "Altura de taza de inodoro"),
    },
    "ESTAC_DIMENSION": {
        "campos": [{"clave": "ancho", "etiqueta": "Ancho del estacionamiento", "unidad": "cm"}],
        "evaluar": _ev_min("ancho", 250, "cm", "Ancho de estacionamiento accesible"),
    },
}


def tiene_regla(criterio_id: str) -> bool:
    return criterio_id in REGLAS


def evaluar(criterio_id: str, valores: dict):
    regla = REGLAS.get(criterio_id)
    if not regla:
        return None, ""
    return regla["evaluar"](valores)
