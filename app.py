import json
import re
from datetime import date, datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

try:
    import pydeck as pdk
    _HAY_PYDECK = True
except Exception:  # noqa: BLE001
    _HAY_PYDECK = False

import bitacora
import config
import norma
import pipeline
import reglas
import registro
import seguimiento

MAX_IMAGENES = 20

st.set_page_config(page_title="Auditor de Accesibilidad", page_icon="♿", layout="centered")

_HTML_AUDIO = """
<div>
  <button id="btnVoz" aria-label="Reproducir o detener lectura"
    style="background:none;border:none;font-size:32px;cursor:pointer;
           line-height:1;padding:4px;display:block;" title="Reproducir / Detener">&#128266;</button>
</div>
<script>
  const texto = __PAYLOAD__; const auto = __AUTO__; const synth = window.speechSynthesis;
  let hablando = false;
  const btn = document.getElementById('btnVoz');
  const ICONO_PLAY = '&#128266;';
  const ICONO_STOP = '&#9209;';
  function elegirVoz(){const v=synth.getVoices();return v.find(x=>x.lang&&x.lang.toLowerCase().startsWith('es'))||null;}
  function leer(){
    synth.cancel();
    const u = new SpeechSynthesisUtterance(texto);
    u.lang='es-ES'; u.rate=0.97;
    const v = elegirVoz(); if(v) u.voice=v;
    u.onstart = () => { hablando=true;  btn.innerHTML=ICONO_STOP; };
    u.onend   = () => { hablando=false; btn.innerHTML=ICONO_PLAY; };
    u.onerror = () => { hablando=false; btn.innerHTML=ICONO_PLAY; };
    synth.speak(u);
  }
  function parar(){ synth.cancel(); hablando=false; btn.innerHTML=ICONO_PLAY; }
  btn.addEventListener('click', () => { hablando ? parar() : leer(); });
  if(typeof synth!=='undefined'){ synth.onvoiceschanged=elegirVoz; }
  if(auto){ setTimeout(leer, 600); }
</script>
"""


def bloque_audio(texto, autoplay_flag):
    texto_limpio = texto.encode("utf-16", "surrogatepass").decode("utf-16", "ignore")
    components.html(
        _HTML_AUDIO
        .replace("__PAYLOAD__", json.dumps(texto_limpio, ensure_ascii=True))
        .replace("__AUTO__", "true" if autoplay_flag else "false"),
        height=50,
    )


def texto_para_audio(resultados):
    partes = []
    for r in resultados:
        partes.append(f"Imagen {r['indice']}.")
        if r.get("resumen"):
            partes.append(r["resumen"])
        hall = r.get("hallazgos", [])
        partes.append("Sin barreras." if not hall else f"{len(hall)} hallazgos.")
        for i, h in enumerate(hall, 1):
            c = norma.buscar_criterio(h.get("criterio_id", ""))
            if c:
                partes.append(f"Hallazgo {i}: {c.elemento}. Incumple {c.norma}, {c.articulo}. Severidad {h.get('severidad','media')}.")
    return " ".join(partes)


def _guardar(archivos, carpeta_base, etiqueta):
    fecha = datetime.now()
    slug = re.sub(r"[^A-Za-z0-9]+", "_", etiqueta).strip("_")[:40] or "item"
    carpeta = carpeta_base / f"{fecha:%Y%m%d_%H%M}_{slug}"
    carpeta.mkdir(parents=True, exist_ok=True)
    guardadas = []
    for i, a in enumerate(archivos, 1):
        destino = carpeta / f"{i:02d}_{re.sub(r'[^A-Za-z0-9._-]+', '_', a.name)}"
        destino.write_bytes(a.getvalue())
        guardadas.append((str(destino), a.name))
    return carpeta, guardadas


def guardar_fotos(archivos, nombre_lugar):
    carpeta, guardadas = _guardar(archivos, config.CARPETA_FOTOS, nombre_lugar)
    try:
        _guardar(archivos, config.CARPETA_SCANAPP, nombre_lugar)
    except Exception:  # noqa: BLE001
        pass
    return carpeta, guardadas


def guardar_evidencias(archivos, etiqueta):
    return _guardar(archivos, config.CARPETA_EVIDENCIAS, etiqueta)


def parse_coords(texto):
    nums = re.findall(r"-?\d+\.\d+|-?\d+", texto or "")
    if len(nums) >= 2:
        try:
            return float(nums[0]), float(nums[1])
        except ValueError:
            return None, None
    return None, None


def render_mapa():
    puntos = [a for a in registro.listar() if a.get("lat") and a.get("lon")]
    if not puntos:
        st.caption("Aún no hay auditorías con ubicación. Agrega coordenadas al programar o auditar.")
        return
    data = []
    for a in puntos:
        color = [46, 125, 50] if a["estado"] == "completada" else [176, 106, 0]
        data.append({"lugar": a["lugar"], "responsable": a.get("responsable") or "—",
                     "usuario": a.get("usuario", ""), "estado": a["estado"],
                     "lat": float(a["lat"]), "lon": float(a["lon"]), "color": color})
    if not _HAY_PYDECK:
        import pandas as pd
        st.map(pd.DataFrame(data)[["lat", "lon"]])
        return
    capa = pdk.Layer("ScatterplotLayer", data=data, get_position="[lon, lat]",
                     get_fill_color="color", get_radius=60, radius_min_pixels=7, pickable=True)
    vista = pdk.ViewState(latitude=data[0]["lat"], longitude=data[0]["lon"], zoom=12)
    st.pydeck_chart(pdk.Deck(layers=[capa], initial_view_state=vista,
                             tooltip={"text": "{lugar}\nResponsable: {responsable}\n"
                                              "Hecho/creado por: {usuario}\nEstado: {estado}"}))
    st.caption("🟢 completada · 🟠 pendiente · pasa el cursor sobre un punto para ver quién lo hace.")


_USUARIO = {"usuario": "scanapp", "rol": "admin"}
usuario = _USUARIO
LISTA_USUARIOS = []
P_EJEC = True
P_SEG_EDIT = True
P_SEG_AV = True

with st.sidebar:
    st.header("♿ Accesibilidad")
    audio_on = st.toggle("🔊 Lectura por voz", value=True)
    autoplay = st.toggle("Leer automáticamente al terminar", value=False)

st.title("♿ Auditor de Accesibilidad")
st.caption("Ejecución · Seguimiento · Pre-diagnóstico con IA")
if not config.GEMINI_API_KEY:
    st.warning("No hay API key configurada. Define GEMINI_API_KEY en un .env "
               "(consíguela gratis en https://aistudio.google.com/apikey).")

tab_ejec, tab_seg = st.tabs(["🔍 Ejecución", "🛠️ Seguimiento"])

with tab_ejec:
    subtab_ia, subtab_cl = st.tabs(["📷 Análisis con IA", "✅ Lista de verificación manual"])

    with subtab_ia:
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre del lugar", placeholder="Ej: Biblioteca Municipal", key="ia_nombre")
            with col2:
                direccion = st.text_input("Dirección", placeholder="Ej: Av. Principal 123", key="ia_dir")
            ecoord = st.text_input("Ubicación (lat, lon) — opcional",
                                   placeholder="Pégala de Google Maps, ej: -33.4489, -70.6693", key="ia_coord")
            archivos = st.file_uploader(f"Fotografías (hasta {MAX_IMAGENES})",
                                        type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="ia_fotos")
            if archivos and len(archivos) > MAX_IMAGENES:
                st.warning(f"Se procesarán solo las primeras {MAX_IMAGENES}."); archivos = archivos[:MAX_IMAGENES]
            if archivos:
                st.caption(f"{len(archivos)} imagen(es).")
                import base64
                thumbs_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;">'
                for i, a in enumerate(archivos):
                    b64 = base64.b64encode(a.getvalue()).decode()
                    ext = a.name.rsplit(".", 1)[-1].lower()
                    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
                    thumbs_html += (
                        f'<div style="text-align:center;">'
                        f'<img src="data:{mime};base64,{b64}" '
                        f'style="width:72px;height:72px;object-fit:cover;border-radius:6px;border:1px solid #ccc;" '
                        f'title="Imagen {i+1}: {a.name}"/>'
                        f'<div style="font-size:10px;color:#666;">{i+1}</div>'
                        f'</div>'
                    )
                thumbs_html += "</div>"
                components.html(thumbs_html, height=max(100, ((len(archivos) - 1) // 10 + 1) * 96))
            if st.button("Analizar y generar informe", type="primary", disabled=not archivos, key="ia_btn"):
                if not nombre.strip():
                    st.error("Ingresa el nombre del lugar."); st.stop()
                carpeta_fotos, imagenes = guardar_fotos(archivos, nombre)
                barra = st.progress(0.0, text="Procesando imágenes…")

                def progreso(hechas, total):
                    barra.progress(hechas / total, text=f"Procesando imagen {hechas} de {total}…")

                try:
                    resultado = pipeline.analizar_varias(imagenes, nombre_lugar=nombre, direccion=direccion, progreso=progreso)
                except Exception as e:  # noqa: BLE001
                    st.error(f"Ocurrió un error: {e}"); st.stop()
                barra.empty()
                elat, elon = parse_coords(ecoord)
                registro.agregar_completada(lugar=nombre, direccion=direccion, usuario=usuario["usuario"],
                                            resultados=resultado["resultados"], pdf=resultado["pdf"],
                                            fotos=[r for r, _ in imagenes], carpeta_fotos=str(carpeta_fotos),
                                            lat=elat, lon=elon)
                seguimiento.agregar_desde_resultados(nombre, resultado["resultados"])
                bitacora.registrar(usuario["usuario"], "auditoría IA", nombre)
                st.session_state["resultado_multi"] = resultado
                st.session_state["carpeta_fotos"] = str(carpeta_fotos)
                st.session_state["_audio_listo"] = True

            resultado = st.session_state.get("resultado_multi")
            if resultado:
                resultados = resultado["resultados"]
                total = sum(len(r.get("hallazgos", [])) for r in resultados)
                _reproducir_auto = autoplay and st.session_state.pop("_audio_listo", False)
                col_ok, col_audio = st.columns([10, 1])
                col_ok.success(f"Listo · {len(resultados)} imagen(es) · {total} hallazgo(s). Pasaron a Seguimiento.")
                if audio_on:
                    with col_audio:
                        bloque_audio(texto_para_audio(resultados), _reproducir_auto)
                for r in resultados:
                    st.markdown(f"### Imagen {r['indice']}: {r['nombre_imagen']}")
                    if r.get("resumen"):
                        st.caption(r["resumen"])
                    for i, h in enumerate(r.get("hallazgos", []), 1):
                        c = norma.buscar_criterio(h.get("criterio_id", ""))
                        if not c:
                            continue
                        sev = (h.get("severidad") or "media").lower()
                        icono = {"alta": "🔴", "media": "🟠", "baja": "🟢"}.get(sev, "⚪")
                        with st.expander(f"{icono} Hallazgo {i}: {c.elemento} (severidad {sev})"):
                            st.markdown(f"**Norma incumplida:** {c.norma} · {c.articulo}")
                            st.markdown(f"**Requisito:** {c.requisito}")
                            st.markdown(f"**Problema observado:** {h.get('descripcion_tecnica', '—')}")
                            st.markdown(f"**Recomendación:** {h.get('recomendacion') or c.recomendacion}")
                pdf_path = Path(resultado["pdf"])
                if pdf_path.exists():
                    with open(pdf_path, "rb") as f:
                        st.download_button("⬇️ Descargar informe PDF", data=f.read(),
                                           file_name=pdf_path.name, mime="application/pdf", type="primary")

    with subtab_cl:
            entorno = st.selectbox("Clasificación del entorno", list(norma.ENTORNOS.keys()),
                                   help="Cada tipo activa un checklist distinto.", key="cl_entorno")
            criterios = norma.criterios_por_entorno(entorno)
            st.caption(f"{len(criterios)} criterios aplican a un entorno de tipo «{entorno}». "
                       "En los que piden medidas, la app marca el incumplimiento sola.")
            categorias = {}
            for c in criterios:
                categorias.setdefault(c.categoria, []).append(c)

            with st.form("form_checklist"):
                cl_lugar = st.text_input("Lugar auditado", key="cl_lugar")
                cl_resp = st.selectbox("Responsable", ["(sin asignar)"] + LISTA_USUARIOS, key="cl_resp")
                for cat, crits in categorias.items():
                    with st.expander(f"{cat.capitalize()} ({len(crits)})"):
                        for c in crits:
                            st.selectbox(f"{c.elemento} — {c.articulo}",
                                         ["No revisado", "Cumple", "No cumple"], key=f"cle_{c.id}")
                            if reglas.tiene_regla(c.id):
                                mcols = st.columns(len(reglas.REGLAS[c.id]["campos"]))
                                for j, campo in enumerate(reglas.REGLAS[c.id]["campos"]):
                                    mcols[j].number_input(
                                        f"{campo['etiqueta']} ({campo['unidad']})",
                                        min_value=0.0, value=0.0, step=1.0, key=f"med_{c.id}_{campo['clave']}")
                            st.text_input("Comentario (opcional)", key=f"clc_{c.id}",
                                          label_visibility="collapsed", placeholder="Comentario (opcional)")
                cl_enlace = st.text_input("Enlace de evidencia (opcional)", key="cl_link")
                cl_files = st.file_uploader("Adjuntar evidencias (fotos / PDF)",
                                            accept_multiple_files=True, key="cl_files")
                ok_cl = st.form_submit_button("Guardar lista de verificación", type="primary")

            if ok_cl:
                _lugar = st.session_state.get("cl_lugar", "").strip()
                _resp  = st.session_state.get("cl_resp", "(sin asignar)")
                _enlace = st.session_state.get("cl_link", "")
                _files  = st.session_state.get("cl_files") or []
                if not _lugar:
                    st.error("Ingresa el lugar auditado.")
                else:
                    rutas = []
                    if _files:
                        _, tuplas = guardar_evidencias(_files, _lugar)
                        rutas = [r for r, _ in tuplas]
                        try:
                            _guardar(_files, config.CARPETA_SCANAPP, _lugar)
                        except Exception:  # noqa: BLE001
                            pass
                    n_no, avisos = 0, []
                    for c in criterios:
                        estado    = st.session_state.get(f"cle_{c.id}", "No revisado")
                        comentario = st.session_state.get(f"clc_{c.id}", "")
                        if reglas.tiene_regla(c.id):
                            med_vals = {
                                campo["clave"]: st.session_state.get(f"med_{c.id}_{campo['clave']}", 0.0)
                                for campo in reglas.REGLAS[c.id]["campos"]
                            }
                            auto_estado, detalle = reglas.evaluar(c.id, med_vals)
                            if auto_estado:
                                avisos.append(f"{c.elemento}: {detalle} → {auto_estado}")
                                if auto_estado == "No cumple":
                                    estado = "No cumple"
                                    comentario = (comentario + " | " if comentario else "") + detalle
                        if estado == "No cumple":
                            seguimiento.agregar(
                                lugar=_lugar, criterio_id=c.id, elemento=c.elemento,
                                norma=c.norma, articulo=c.articulo, severidad="media",
                                descripcion=comentario or "Marcado como 'No cumple' en checklist.",
                                origen="checklist",
                                responsable=("" if _resp == "(sin asignar)" else _resp),
                                evidencias=rutas, enlace=_enlace,
                            )
                            n_no += 1
                    bitacora.registrar(usuario["usuario"], "checklist",
                                       f"{_lugar} ({entorno}) · {n_no} no conformidad(es)")
                    st.success(f"Lista guardada · {n_no} no conformidad(es) enviadas a Seguimiento.")
                    if rutas:
                        st.caption(f"📎 {len(rutas)} archivo(s) adjuntado(s) a los hallazgos.")
                    for av in avisos:
                        (st.error if av.endswith("No cumple") else st.success)(av)

with tab_seg:
    s = seguimiento.resumen()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Abiertas", s["abiertos"]); c2.metric("En progreso", s["en_progreso"])
    c3.metric("Resueltas", s["resueltos"]); c4.metric("Avance prom.", f"{s['avance_promedio']}%")
    filtro = st.selectbox("Filtrar por estado", ["todas", "abierto", "en_progreso", "resuelto"])
    items = seguimiento.listar()
    if filtro != "todas":
        items = [h for h in items if h.get("estado") == filtro]
    if not items:
        st.info("No hay no conformidades para mostrar.")
    iconos = {"abierto": "🔴", "en_progreso": "🟡", "resuelto": "🟢"}

    from collections import OrderedDict
    lugares_dict: dict = OrderedDict()
    for h in reversed(items):
        lugar = h.get("lugar", "—")
        lugares_dict.setdefault(lugar, []).append(h)

    for lugar, hallazgos in lugares_dict.items():
        estados_lugar = [h.get("estado", "abierto") for h in hallazgos]
        icono_lugar = ("🔴" if "abierto" in estados_lugar
                       else "🟡" if "en_progreso" in estados_lugar else "🟢")
        n_total = len(hallazgos)
        n_resueltos = sum(1 for h in hallazgos if h.get("estado") == "resuelto")
        with st.expander(f"{icono_lugar} 📍 {lugar}  —  {n_resueltos}/{n_total} resueltos"):
            for h in hallazgos:
                sev = (h.get("severidad") or "media").lower()
                icono_h = iconos.get(h.get("estado"), "⚪")
                sev_badge = {"alta": "🔴 Alta", "media": "🟠 Media", "baja": "🟢 Baja"}.get(sev, sev)
                with st.expander(
                    f"{icono_h} **{h.get('elemento','—')}** · {sev_badge} · "
                    f"{h.get('norma','')} {h.get('articulo','')} · "
                    f"avance {h.get('avance',0)}%",
                    expanded=False
                ):
                    i1, i2, i3 = st.columns(3)
                    i1.caption(f"**Origen:** {h.get('origen','—')}")
                    i2.caption(f"**Estado:** {h.get('estado','—')}")
                    i3.caption(f"**Creada:** {h.get('creada','')[:10]}")
                    if h.get("descripcion"):
                        st.info(h["descripcion"], icon="📋")
                    if h.get("enlace"):
                        st.markdown(f"🔗 [Evidencia enlazada]({h['enlace']})")
                    if h.get("evidencias"):
                        st.caption("📎 " + ", ".join(Path(e).name for e in h["evidencias"]))

                    if not (P_SEG_EDIT or P_SEG_AV):
                        st.caption(f"Avance: {h.get('avance',0)}%  (solo lectura)")
                        continue

                    with st.form(f"form_seg_{h['id']}"):
                        col_a, col_b = st.columns(2)
                        if P_SEG_EDIT:
                            est = col_a.selectbox("Estado", seguimiento.ESTADOS,
                                                  index=seguimiento.ESTADOS.index(h.get("estado", "abierto")))
                            resp = col_b.selectbox("Responsable", ["(sin asignar)"] + LISTA_USUARIOS,
                                                   index=(["(sin asignar)"] + LISTA_USUARIOS).index(h["responsable"])
                                                   if h.get("responsable") in LISTA_USUARIOS else 0)
                            venc = st.date_input("Plazo de corrección",
                                                 value=date.fromisoformat(h["vencimiento"]) if h.get("vencimiento") else date.today())
                        else:
                            est, resp, venc = h.get("estado", "abierto"), h.get("responsable", ""), None
                        av = st.slider("Avance (%)", 0, 100, int(h.get("avance", 0)), step=10)
                        plan = st.text_area("Plan de acción correctiva", value=h.get("plan_accion", ""),
                                            height=80, placeholder="Describe qué se hará para corregir esto…")
                        cc = st.columns(2)
                        guardar = cc[0].form_submit_button("💾 Guardar", type="primary")
                        borrar = cc[1].form_submit_button("🗑️ Eliminar") if P_SEG_EDIT else False
                    if guardar:
                        campos = {"avance": av, "plan_accion": plan}
                        if P_SEG_EDIT:
                            campos.update(estado=est, responsable=("" if resp == "(sin asignar)" else resp),
                                          vencimiento=venc.isoformat())
                        seguimiento.actualizar(h["id"], **campos)
                        bitacora.registrar(usuario["usuario"], "actualizar hallazgo",
                                           f"{h.get('lugar')} · {h.get('elemento')} · avance {av}%")
                        st.success("Actualizado."); st.rerun()
                    if borrar:
                        seguimiento.eliminar(h["id"])
                        bitacora.registrar(usuario["usuario"], "eliminar hallazgo", h.get("elemento", ""))
                        st.rerun()
