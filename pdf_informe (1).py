from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

import config
from norma import buscar_criterio

AZUL = colors.HexColor("#1f3a5f")
GRIS = colors.HexColor("#5b6470")
ROJO = colors.HexColor("#b3261e")
NARANJO = colors.HexColor("#b06a00")
VERDE = colors.HexColor("#2e7d32")

_COLOR_SEVERIDAD = {"alta": ROJO, "media": NARANJO, "baja": VERDE}


def _estilos():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("TituloDoc", parent=s["Title"], textColor=AZUL, fontSize=18, spaceAfter=4))
    s.add(ParagraphStyle("Subtitulo", parent=s["Normal"], textColor=GRIS, fontSize=10, spaceAfter=12))
    s.add(ParagraphStyle("Seccion", parent=s["Heading2"], textColor=AZUL, fontSize=13, spaceBefore=14, spaceAfter=6))
    s.add(ParagraphStyle("Cuerpo", parent=s["Normal"], fontSize=10, leading=14, alignment=TA_JUSTIFY))
    s.add(ParagraphStyle("Etiqueta", parent=s["Normal"], fontSize=8, textColor=GRIS, alignment=TA_LEFT))
    s.add(ParagraphStyle("Dato", parent=s["Normal"], fontSize=10, leading=13))
    s.add(ParagraphStyle("Hallazgo", parent=s["Heading3"], textColor=AZUL, fontSize=11, spaceBefore=10, spaceAfter=2))
    s.add(ParagraphStyle("Nota", parent=s["Normal"], fontSize=8, textColor=GRIS, leading=11, alignment=TA_JUSTIFY))
    return s


def _enriquecer(hallazgos: list[dict]) -> list[dict]:
    enriquecidos = []
    for h in hallazgos:
        criterio = buscar_criterio(h.get("criterio_id", ""))
        if criterio is None:
            continue
        enriquecidos.append({**h, "criterio": criterio})
    return enriquecidos


def _render_hallazgos(story, s, resumen: str, hallazgos: list[dict]):
    if resumen:
        story.append(Paragraph(f"<b>Resumen:</b> {resumen}", s["Cuerpo"]))
        story.append(Spacer(1, 6))

    enriquecidos = _enriquecer(hallazgos)
    if not enriquecidos:
        story.append(Paragraph(
            "No se identificaron barreras asociables a los criterios del catálogo "
            "normativo. Esto no descarta la necesidad de una inspección en terreno.",
            s["Cuerpo"]))
        return

    for i, h in enumerate(enriquecidos, 1):
        c = h["criterio"]
        sev = (h.get("severidad") or "media").lower()
        color_sev = _COLOR_SEVERIDAD.get(sev, GRIS)

        story.append(Paragraph(f"{i}. {c.elemento} — {c.norma}, {c.articulo}", s["Hallazgo"]))
        filas = [
            [Paragraph("Severidad", s["Etiqueta"]),
             Paragraph(f'<font color="{color_sev.hexval()}"><b>{sev.upper()}</b></font>', s["Dato"])],
            [Paragraph("Certeza", s["Etiqueta"]),
             Paragraph((h.get("nivel_certeza") or "—").replace("_", " "), s["Dato"])],
            [Paragraph("Discapacidad afectada", s["Etiqueta"]),
             Paragraph(", ".join(c.discapacidades), s["Dato"])],
            [Paragraph("Requisito normativo", s["Etiqueta"]),
             Paragraph(c.requisito, s["Cuerpo"])],
            [Paragraph("Problema observado", s["Etiqueta"]),
             Paragraph(h.get("descripcion_tecnica", "—"), s["Cuerpo"])],
            [Paragraph("Recomendación", s["Etiqueta"]),
             Paragraph(h.get("recomendacion") or c.recomendacion, s["Cuerpo"])],
        ]
        tabla = Table(filas, colWidths=[4 * cm, 12 * cm])
        tabla.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#eeeeee")),
            ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(tabla)
        story.append(Spacer(1, 4))


def _ficha(story, s, filas):
    t = Table(filas, colWidths=[3.5 * cm, 12.5 * cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#e0e0e0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


def _encabezado(story, s):
    story.append(Paragraph("Informe técnico de accesibilidad universal", s["TituloDoc"]))
    story.append(Paragraph("Pre-diagnóstico asistido por IA · sujeto a validación profesional", s["Subtitulo"]))
    story.append(HRFlowable(width="100%", color=AZUL, thickness=1.2, spaceAfter=10))


def _disclaimer(story, s):
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#dddddd"), thickness=0.5, spaceAfter=6))
    story.append(Paragraph(
        "Este documento es un <b>pre-diagnóstico generado con apoyo de inteligencia "
        "artificial</b> a partir de fotografías. No constituye una certificación "
        "oficial. Las mediciones (pendientes, anchos, alturas) y la aplicabilidad de "
        "cada artículo deben ser verificadas en terreno por un profesional competente "
        "antes de cualquier presentación formal ante la Dirección de Obras Municipales. "
        "Las referencias normativas provienen del catálogo interno de la plataforma y "
        "deben contrastarse con el texto oficial vigente de la OGUC y las normas NCh "
        "aplicables.",
        s["Nota"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Generado por {config.ORGANIZACION} · Modelo: {config.MODELO_IA}", s["Nota"]))


def _nueva_ruta(nombre_lugar: str, fecha: datetime) -> Path:
    slug = "".join(c if c.isalnum() else "_" for c in nombre_lugar)[:40]
    return config.CARPETA_SALIDA / f"informe_{slug}_{fecha:%Y%m%d_%H%M}.pdf"


def generar_pdf(*, nombre_lugar, direccion, resumen, hallazgos, ruta_salida=None) -> Path:
    fecha = datetime.now()
    ruta_salida = Path(ruta_salida) if ruta_salida else _nueva_ruta(nombre_lugar, fecha)

    s = _estilos()
    doc = SimpleDocTemplate(
        str(ruta_salida), pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
        title=f"Informe de accesibilidad - {nombre_lugar}",
    )
    story = []
    _encabezado(story, s)
    _ficha(story, s, [
        [Paragraph("LUGAR", s["Etiqueta"]), Paragraph(nombre_lugar or "—", s["Dato"])],
        [Paragraph("DIRECCIÓN", s["Etiqueta"]), Paragraph(direccion or "—", s["Dato"])],
        [Paragraph("FECHA", s["Etiqueta"]), Paragraph(fecha.strftime("%d-%m-%Y %H:%M"), s["Dato"])],
        [Paragraph("HALLAZGOS", s["Etiqueta"]), Paragraph(str(len(hallazgos)), s["Dato"])],
    ])
    story.append(Paragraph("Hallazgos y referencias normativas", s["Seccion"]))
    _render_hallazgos(story, s, resumen, hallazgos)
    _disclaimer(story, s)
    doc.build(story)
    return ruta_salida


def generar_pdf_multiple(*, nombre_lugar, direccion, resultados: list[dict], ruta_salida=None) -> Path:
    fecha = datetime.now()
    ruta_salida = Path(ruta_salida) if ruta_salida else _nueva_ruta(nombre_lugar, fecha)
    total = sum(len(r.get("hallazgos", [])) for r in resultados)

    s = _estilos()
    doc = SimpleDocTemplate(
        str(ruta_salida), pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
        title=f"Informe de accesibilidad - {nombre_lugar}",
    )
    story = []
    _encabezado(story, s)
    _ficha(story, s, [
        [Paragraph("LUGAR", s["Etiqueta"]), Paragraph(nombre_lugar or "—", s["Dato"])],
        [Paragraph("DIRECCIÓN", s["Etiqueta"]), Paragraph(direccion or "—", s["Dato"])],
        [Paragraph("FECHA", s["Etiqueta"]), Paragraph(fecha.strftime("%d-%m-%Y %H:%M"), s["Dato"])],
        [Paragraph("IMÁGENES", s["Etiqueta"]), Paragraph(str(len(resultados)), s["Dato"])],
        [Paragraph("HALLAZGOS TOTALES", s["Etiqueta"]), Paragraph(str(total), s["Dato"])],
    ])

    for idx, r in enumerate(resultados):
        nombre_img = r.get("nombre_imagen", f"imagen_{r.get('indice', idx + 1)}")
        story.append(Paragraph(f"Imagen {r.get('indice', idx + 1)} — {nombre_img}", s["Seccion"]))
        `_render_hallazgos(story, s, r.get("resumen", ""), r.get("hallazgos", []))
        if idx < len(resultados) - 1:
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", color=colors.HexColor("#e8e8e8"), thickness=0.5, spaceAfter=2))

    _disclaimer(story, s)
    doc.build(story)
    return ruta_salida
