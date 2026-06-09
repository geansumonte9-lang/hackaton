import json
import secrets
from datetime import datetime

import config

ARCHIVO = config.RAIZ / "hallazgos.json"
ESTADOS = ["abierto", "en_progreso", "resuelto"]


def _cargar() -> list:
    if ARCHIVO.exists():
        return json.loads(ARCHIVO.read_text(encoding="utf-8"))
    return []


def _guardar(data: list):
    ARCHIVO.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def agregar(*, lugar, criterio_id="", elemento="", norma="", articulo="",
            severidad="media", descripcion="", origen="manual",
            responsable="", vencimiento=None, plan_accion="",
            evidencias=None, enlace=""):
    data = _cargar()
    data.append({
        "id": secrets.token_hex(6),
        "creada": datetime.now().isoformat(timespec="minutes"),
        "lugar": lugar,
        "criterio_id": criterio_id,
        "elemento": elemento,
        "norma": norma,
        "articulo": articulo,
        "severidad": (severidad or "media").lower(),
        "descripcion": descripcion,
        "origen": origen,
        "estado": "abierto",
        "avance": 0,
        "plan_accion": plan_accion,
        "responsable": responsable,
        "vencimiento": vencimiento,
        "evidencias": evidencias or [],
        "enlace": enlace,
    })
    _guardar(data)


def agregar_desde_resultados(lugar: str, resultados: list):
    import norma as _norma
    data = _cargar()
    for r in resultados:
        for h in r.get("hallazgos", []):
            c = _norma.buscar_criterio(h.get("criterio_id", ""))
            if c is None:
                continue
            data.append({
                "id": secrets.token_hex(6),
                "creada": datetime.now().isoformat(timespec="minutes"),
                "lugar": lugar,
                "criterio_id": c.id,
                "elemento": c.elemento,
                "norma": c.norma,
                "articulo": c.articulo,
                "severidad": (h.get("severidad") or "media").lower(),
                "descripcion": h.get("descripcion_tecnica", ""),
                "origen": "IA",
                "estado": "abierto",
                "avance": 0,
                "plan_accion": "",
                "responsable": "",
                "vencimiento": None,
                "evidencias": [],
                "enlace": "",
            })
    _guardar(data)


def listar() -> list:
    return _cargar()


def actualizar(id_: str, **campos):
    data = _cargar()
    for h in data:
        if h.get("id") == id_:
            for k, v in campos.items():
                if v is not None:
                    h[k] = v
            if h.get("estado") == "resuelto":
                h["avance"] = 100
            elif h.get("avance", 0) >= 100 and h.get("estado") != "resuelto":
                h["estado"] = "resuelto"
    _guardar(data)


def eliminar(id_: str):
    _guardar([h for h in _cargar() if h.get("id") != id_])


def resumen() -> dict:
    data = _cargar()
    abiertos = sum(1 for h in data if h.get("estado") == "abierto")
    en_progreso = sum(1 for h in data if h.get("estado") == "en_progreso")
    resueltos = sum(1 for h in data if h.get("estado") == "resuelto")
    avance = round(sum(h.get("avance", 0) for h in data) / len(data)) if data else 0
    return {
        "total": len(data),
        "abiertos": abiertos,
        "en_progreso": en_progreso,
        "resueltos": resueltos,
        "avance_promedio": avance,
    }
