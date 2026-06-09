import hashlib
import hmac
import json
import re
import secrets

import config

ARCHIVO_USUARIOS = config.RAIZ / "usuarios.json"
MAX_CUENTAS = 10
ITERACIONES = 200_000

EMAIL_RE = re.compile(r"^[^@\s]+@gmail\.com$", re.IGNORECASE)

ROLES_ASIGNABLES = ["auditor", "auditado", "lectura"]

_PERMISOS = {
    "admin":    {"cuentas", "planificar", "ejecutar", "seguimiento_editar", "seguimiento_avance", "ver"},
    "auditor":  {"planificar", "ejecutar", "seguimiento_editar", "seguimiento_avance", "ver"},
    "usuario":  {"planificar", "ejecutar", "seguimiento_editar", "seguimiento_avance", "ver"},
    "auditado": {"ver", "seguimiento_avance"},
    "lectura":  {"ver"},
}


def puede(rol: str, accion: str) -> bool:
    return accion in _PERMISOS.get(rol, {"ver"})


def _cargar() -> dict:
    if ARCHIVO_USUARIOS.exists():
        return json.loads(ARCHIVO_USUARIOS.read_text(encoding="utf-8"))
    return {}


def _guardar(data: dict):
    ARCHIVO_USUARIOS.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _hash(password: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), ITERACIONES
    )
    return salt, dk.hex()


def _validar_email(email: str) -> str:
    email = (email or "").strip()
    if not EMAIL_RE.match(email):
        raise ValueError("El correo debe ser una dirección Gmail válida (ejemplo@gmail.com).")
    return email.lower()


def _validar_password(password: str):
    if not password or len(password) < 4:
        raise ValueError("La contraseña debe tener al menos 4 caracteres.")


def hay_usuarios() -> bool:
    return len(_cargar()) > 0


def existe_admin() -> bool:
    return any(u.get("rol") == "admin" for u in _cargar().values())


def contar() -> int:
    return len(_cargar())


def listar_usuarios() -> dict:
    return {
        u: {"rol": info.get("rol", "usuario"), "email": info.get("email", "—"),
            "rut": info.get("rut", "")}
        for u, info in _cargar().items()
    }


def crear_usuario(usuario: str, password: str, email: str, rol: str = "usuario", rut: str = ""):
    data = _cargar()
    usuario = usuario.strip().lower()

    if not usuario:
        raise ValueError("El nombre de usuario es obligatorio.")
    if rol != "admin" and rol not in ROLES_ASIGNABLES:
        raise ValueError("Rol no válido.")
    _validar_password(password)
    email = _validar_email(email)
    if usuario in data:
        raise ValueError("Ese nombre de usuario ya existe.")
    if len(data) >= MAX_CUENTAS:
        raise ValueError(f"Se alcanzó el máximo de {MAX_CUENTAS} cuentas.")
    if rol == "admin" and existe_admin():
        raise ValueError("Ya existe una cuenta administradora.")

    salt, h = _hash(password)
    data[usuario] = {"rol": rol, "email": email, "rut": rut.strip(), "salt": salt, "hash": h}
    _guardar(data)


def verificar(usuario: str, password: str) -> dict | None:
    data = _cargar()
    usuario = usuario.strip().lower()
    info = data.get(usuario)
    if not info:
        return None
    _, h = _hash(password, info["salt"])
    if hmac.compare_digest(h, info["hash"]):
        return {"usuario": usuario, "rol": info.get("rol", "usuario")}
    return None


def eliminar_usuario(usuario: str):
    data = _cargar()
    usuario = usuario.strip().lower()
    info = data.get(usuario)
    if not info:
        raise ValueError("La usuaria no existe.")
    if info.get("rol") == "admin":
        raise ValueError("No se puede eliminar la cuenta administradora.")
    del data[usuario]
    _guardar(data)


def renombrar_usuario(viejo: str, nuevo: str):
    data = _cargar()
    viejo = viejo.strip().lower()
    nuevo = nuevo.strip().lower()
    if viejo not in data:
        raise ValueError("La usuaria a renombrar no existe.")
    if not nuevo:
        raise ValueError("El nuevo nombre no puede estar vacío.")
    if nuevo == viejo:
        return
    if nuevo in data:
        raise ValueError("Ya existe una cuenta con el nuevo nombre.")
    data[nuevo] = data.pop(viejo)
    _guardar(data)


def cambiar_email(usuario: str, email: str):
    data = _cargar()
    usuario = usuario.strip().lower()
    if usuario not in data:
        raise ValueError("La usuaria no existe.")
    data[usuario]["email"] = _validar_email(email)
    _guardar(data)


def cambiar_password(usuario: str, password: str):
    data = _cargar()
    usuario = usuario.strip().lower()
    if usuario not in data:
        raise ValueError("La usuaria no existe.")
    _validar_password(password)
    salt, h = _hash(password)
    data[usuario]["salt"] = salt
    data[usuario]["hash"] = h
    _guardar(data)


def restablecer_password(usuario: str, email: str, nueva_password: str):
    data = _cargar()
    usuario = usuario.strip().lower()
    email = (email or "").strip().lower()
    info = data.get(usuario)
    if not info or info.get("email", "").lower() != email:
        raise ValueError("El usuario y el correo no coinciden con ninguna cuenta.")
    _validar_password(nueva_password)
    salt, h = _hash(nueva_password)
    info["salt"] = salt
    info["hash"] = h
    _guardar(data)
