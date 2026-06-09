import json
import secrets
from datetime import date, datetime, timedelta

import config

ARCHIVO = config.RAIZ / "auditorias.json"
DIAS_POR_VENCER = 7


def _cargar() -> list:
    if ARCHIVO.exists():
        return json.loads(ARCHIVO.read_text(encoding="utf-8"))
    return []


def _guardar(data: list):
    ARCHIVO.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _parse_fecha(s: str | None):
    try:
        return date.fromisoformat(s) if s else None
    except (ValueError, TypeError):
        return None


def _contar(resultados: list) -> dict:
    sev = {"alta": 0, "media": 0, "baja": 0}
    sin_hallazgos = 0
    imgs = 0
    total_hallazgos = 0
    for r in resultados:
        imgs += 1
        hs = r.get("hallazgos", [])
        if not hs:
            sin_hallazgos += 1
        for h in hs:
            total_hallazgos += 1
            s = (h.get("severidad") or "media").lower()
            sev[s] = sev.get(s, 0) + 1 if s in sev else sev["media"] + 1
            if s not in sev:
                sev["media"] += 1
    return {
        "severidades": {"alta": sev["alta"], "media": sev["media"], "baja": sev["baja"]},
        "imagenes_sin_hallazgos": sin_hallazgos,
        "num_imagenes": imgs,
        "num_hallazgos": total_hallazgos,
    }


def agregar_completada(*, lugar, direccion, usuario, resultados, pdf=None,
                       fotos=None, carpeta_fotos=None, lat=None, lon=None, tipo_espacio=""):
    data = _cargar()
    c = _contar(resultados)
    estado_cumplimiento = "Aprobado" if c["num_hallazgos"] == 0 else "Rechazado"
    data.append({
        "id": secrets.token_hex(6),
        "lugar": lugar, "direccion": direccion,
        "tipo_espacio": tipo_espacio,
        "creada": datetime.now().isoformat(timespec="minutes"),
        "usuario": usuario,
        "estado": "completada",
        "estado_cumplimiento": estado_cumplimiento,
        "vencimiento": None,
        "lat": lat, "lon": lon,
        "pdf": str(pdf) if pdf else None,
        "fotos": fotos or [],
        "carpeta_fotos": carpeta_fotos,
        **c,
    })
    _guardar(data)


def agregar_pendiente(*, lugar, direccion, usuario, vencimiento, responsable="", alcance="",
                      lat=None, lon=None):
    data = _cargar()
    data.append({
        "id": secrets.token_hex(6),
        "lugar": lugar, "direccion": direccion,
        "creada": datetime.now().isoformat(timespec="minutes"),
        "usuario": usuario,
        "estado": "pendiente",
        "vencimiento": vencimiento,
        "responsable": responsable,
        "alcance": alcance,
        "lat": lat, "lon": lon,
        "pdf": None,
        "severidades": {"alta": 0, "media": 0, "baja": 0},
        "imagenes_sin_hallazgos": 0, "num_imagenes": 0, "num_hallazgos": 0,
    })
    _guardar(data)


def eliminar(id_: str):
    _guardar([a for a in _cargar() if a.get("id") != id_])


def marcar_completada(id_: str):
    data = _cargar()
    for a in data:
        if a.get("id") == id_:
            a["estado"] = "completada"
    _guardar(data)


def listar() -> list:
    return _cargar()


def _vencidas(pendientes: list) -> int:
    hoy = date.today()
    return sum(1 for a in pendientes
               if (_parse_fecha(a.get("vencimiento")) and _parse_fecha(a["vencimiento"]) < hoy))


def _por_vencer(pendientes: list) -> int:
    hoy = date.today()
    limite = hoy + timedelta(days=DIAS_POR_VENCER)
    return sum(1 for a in pendientes
               if (_parse_fecha(a.get("vencimiento")) and hoy <= _parse_fecha(a["vencimiento"]) <= limite))


def kpis() -> dict:
    data = _cargar()
    completadas = [a for a in data if a.get("estado") == "completada"]
    pendientes = [a for a in data if a.get("estado") == "pendiente"]

    total_imgs = sum(a.get("num_imagenes", 0) for a in completadas)
    sin = sum(a.get("imagenes_sin_hallazgos", 0) for a in completadas)
    cumplimiento = round(100 * sin / total_imgs) if total_imgs else None

    altas = sum(a.get("severidades", {}).get("alta", 0) for a in completadas)
    medias = sum(a.get("severidades", {}).get("media", 0) for a in completadas)
    vencidas = _vencidas(pendientes)
    por_vencer = _por_vencer(pendientes)

    if altas > 0 or vencidas > 0:
        riesgo = "alto"
    elif medias > 0 or por_vencer > 0:
        riesgo = "medio"
    else:
        riesgo = "bajo"

    return {
        "cumplimiento": cumplimiento,
        "completadas": len(completadas),
        "pendientes": len(pendientes),
        "total": len(data),
        "hallazgos_altos": altas,
        "hallazgos_medios": medias,
        "riesgo": riesgo,
    }


def alertas() -> list:
    data = _cargar()
    completadas = [a for a in data if a.get("estado") == "completada"]
    pendientes = [a for a in data if a.get("estado") == "pendiente"]
    als = []

    altas = sum(a.get("severidades", {}).get("alta", 0) for a in completadas)
    if altas:
        als.append({"nivel": "rojo",
                    "mensaje": f"{altas} hallazgo(s) crítico(s) de severidad alta."})

    vencidas = _vencidas(pendientes)
    if vencidas:
        als.append({"nivel": "rojo",
                    "mensaje": f"{vencidas} tarea(s) de auditoría vencida(s)."})

    por_vencer = _por_vencer(pendientes)
    if por_vencer:
        als.append({"nivel": "amarillo",
                    "mensaje": f"{por_vencer} tarea(s) por vencer en los próximos {DIAS_POR_VENCER} días."})

    medias = sum(a.get("severidades", {}).get("media", 0) for a in completadas)
    if medias and not altas:
        als.append({"nivel": "amarillo",
                    "mensaje": f"{medias} hallazgo(s) de severidad media por revisar."})

    if not als:
        als.append({"nivel": "verde",
                    "mensaje": "Sin hallazgos críticos ni tareas vencidas. Todo al día."})
    return als
