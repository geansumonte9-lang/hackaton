from pathlib import Path

import config
import gemini_client
import pdf_informe


def _filtrar_por_confianza(detecciones: dict) -> dict:
    elementos = detecciones.get("elementos_detectados", [])
    filtrados = [
        e for e in elementos
        if float(e.get("confianza", 0)) >= config.CONFIANZA_MINIMA
    ]
    return {**detecciones, "elementos_detectados": filtrados}


def _analizar_una(ruta_imagen) -> dict:
    detecciones = gemini_client.analizar_imagen(ruta_imagen)
    return _filtrar_por_confianza(detecciones)


def analizar(ruta_imagen, *, nombre_lugar, direccion="", ruta_pdf=None) -> dict:
    detecciones = _analizar_una(ruta_imagen)
    informe = gemini_client.redactar_informe(detecciones)
    pdf = pdf_informe.generar_pdf(
        nombre_lugar=nombre_lugar,
        direccion=direccion,
        resumen=informe.get("resumen", ""),
        hallazgos=informe.get("hallazgos", []),
        ruta_salida=ruta_pdf,
    )
    return {
        "detecciones": detecciones,
        "informe": {"resumen": informe.get("resumen", ""), "hallazgos": informe.get("hallazgos", [])},
        "pdf": pdf,
    }


def analizar_varias(imagenes, *, nombre_lugar, direccion="", ruta_pdf=None, progreso=None) -> dict:
    total_pasos = len(imagenes) + 1

    items_deteccion = []
    for idx, (ruta, nombre_img) in enumerate(imagenes, 1):
        detecciones = _analizar_una(ruta)
        items_deteccion.append({
            "indice": idx,
            "nombre_imagen": nombre_img,
            "detecciones": detecciones,
        })
        if progreso:
            progreso(idx, total_pasos)

    sintesis = gemini_client.sintetizar_edificio(
        items_deteccion,
        nombre_lugar=nombre_lugar,
    )
    if progreso:
        progreso(total_pasos, total_pasos)

    hallazgos_edificio = sintesis.get("hallazgos", [])
    resumen_edificio   = sintesis.get("resumen", sintesis.get("resumen_edificio", ""))

    todos_elementos = []
    for item in items_deteccion:
        todos_elementos.extend(item["detecciones"].get("elementos_detectados", []))
    detecciones_combinadas = {
        "descripcion_general": f"Análisis de {len(imagenes)} fotografía(s) del edificio.",
        "elementos_detectados": todos_elementos,
    }

    resultados = [{
        "indice": 1,
        "nombre_imagen": f"{nombre_lugar} — consolidado ({len(imagenes)} foto(s))",
        "resumen": resumen_edificio,
        "hallazgos": hallazgos_edificio,
        "detecciones": detecciones_combinadas,
    }]

    pdf = pdf_informe.generar_pdf_multiple(
        nombre_lugar=nombre_lugar,
        direccion=direccion,
        resultados=resultados,
        ruta_salida=ruta_pdf,
    )
    return {"resultados": resultados, "pdf": pdf}
