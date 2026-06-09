import hashlib
import json
from datetime import datetime

import config

ARCHIVO = config.RAIZ / "bitacora.json"
MAX_ENTRADAS = 5000


def _cargar() -> list:
    if ARCHIVO.exists():
        return json.loads(ARCHIVO.read_text(encoding="utf-8"))
    return []


def _guardar(data: list):
    ARCHIVO.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _hash_entrada(e: dict) -> str:
    base = {
        "fecha": e["fecha"], "usuario": e["usuario"], "accion": e["accion"],
        "detalle": e.get("detalle", ""), "prev_hash": e["prev_hash"],
    }
    crudo = json.dumps(base, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()


def registrar(usuario: str, accion: str, detalle: str = ""):
    data = _cargar()
    prev = data[-1]["hash"] if (data and "hash" in data[-1]) else "GENESIS"
    e = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "usuario": usuario, "accion": accion, "detalle": detalle,
        "prev_hash": prev,
    }
    e["hash"] = _hash_entrada(e)
    data.append(e)
    _guardar(data[-MAX_ENTRADAS:])


def leer(limite: int = 100) -> list:
    return list(reversed(_cargar()))[:limite]


def verificar() -> tuple:
    data = _cargar()
    prev_hash = None
    for i, e in enumerate(data):
        if "hash" not in e:
            prev_hash = None
            continue
        if _hash_entrada(e) != e["hash"]:
            return False, i, len(data)
        if prev_hash is not None and e.get("prev_hash") != prev_hash:
            return False, i, len(data)
        prev_hash = e["hash"]
    return True, None, len(data)
