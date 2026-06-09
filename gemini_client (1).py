import json
import mimetypes
import time
from pathlib import Path

from google import genai
from google.genai import types

import config
import prompts
from norma import catalogo_para_prompt


def _crear_cliente() -> genai.Client:
    if not config.GEMINI_API_KEY:
        raise RuntimeError(
            "Falta la API key. Define la variable de entorno GEMINI_API_KEY "
            "(consíguela gratis en https://aistudio.google.com/apikey)."
        )
    return genai.Client(api_key=config.GEMINI_API_KEY)


_TRANSITORIOS = ("503", "unavailable", "overloaded", "high demand",
                 "429", "resource_exhausted")


def _es_transitorio(e: Exception) -> bool:
    msg = str(e).lower()
    return any(t in msg for t in _TRANSITORIOS)


def _generar_con_reintentos(cliente, *, intentos: int = 4, espera_base: float = 2.0, **kwargs):
    ultimo_error: Exception | None = None
    for intento in range(intentos):
        try:
            return cliente.models.generate_content(**kwargs)
        except Exception as e:  # noqa: BLE001
            if not _es_transitorio(e) or intento == intentos - 1:
                raise
            ultimo_error = e
            time.sleep(espera_base * (2 ** intento))
    if ultimo_error:
        raise ultimo_error


def _limpiar_json(texto: str) -> dict:
    t = texto.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        t = t.rsplit("```", 1)[0]
    return json.loads(t.strip())


def analizar_imagen(ruta_imagen: str | Path) -> dict:
    ruta = Path(ruta_imagen)
    datos = ruta.read_bytes()
    mime = mimetypes.guess_type(ruta.name)[0] or "image/jpeg"

    cliente = _crear_cliente()
    respuesta = _generar_con_reintentos(
        cliente,
        model=config.MODELO_IA,
        contents=[
            types.Part.from_bytes(data=datos, mime_type=mime),
            prompts.PROMPT_VISION,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    return _limpiar_json(respuesta.text)


def redactar_informe(detecciones: dict) -> dict:
    prompt = prompts.PROMPT_REDACCION.format(
        catalogo=catalogo_para_prompt(),
        detecciones=json.dumps(detecciones, ensure_ascii=False, indent=2),
    )

    cliente = _crear_cliente()
    respuesta = _generar_con_reintentos(
        cliente,
        model=config.MODELO_IA,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )
    return _limpiar_json(respuesta.text)


def sintetizar_edificio(todas_detecciones: list[dict], *, nombre_lugar: str) -> dict:
    import json as _json
    from norma import catalogo_para_prompt as _cat

    partes = []
    for item in todas_detecciones:
        partes.append(
            f"--- Foto {item['indice']}: {item['nombre_imagen']} ---\n"
            + _json.dumps(item["detecciones"], ensure_ascii=False, indent=2)
        )
    detecciones_todas = "\n\n".join(partes)

    prompt = prompts.PROMPT_SINTESIS_EDIFICIO.format(
        n_fotos=len(todas_detecciones),
        nombre_lugar=nombre_lugar,
        catalogo=_cat(),
        detecciones_todas=detecciones_todas,
    )

    cliente = _crear_cliente()
    respuesta = _generar_con_reintentos(
        cliente,
        model=config.MODELO_IA,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    data = _limpiar_json(respuesta.text)
    if "resumen_edificio" in data and "resumen" not in data:
        data["resumen"] = data["resumen_edificio"]
    return data
