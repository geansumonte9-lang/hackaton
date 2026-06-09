from dataclasses import dataclass
from typing import List

MARCO_LEGAL = (
    "Ley 20.422 · Ley 21.089 · DFL 458 (LGUC) · OGUC (DS 50 / DS 30) · "
    "NCh 3269 · NCh 3271 · NCh 3616"
)

PRINCIPIO_MANDATORIO = (
    "Diseño universal autónomo e independiente: se prohíbe la asistencia "
    "obligatoria por terceros y el uso de accesos secundarios o de servicio "
    "para resolver la accesibilidad."
)


@dataclass
class CriterioNormativo:
    id: str
    categoria: str
    elemento: str
    norma: str
    articulo: str
    requisito: str
    discapacidades: List[str]
    pistas_visuales: str
    recomendacion: str


CATALOGO: List[CriterioNormativo] = [

    CriterioNormativo(
        id="RUTA_ANCHO",
        categoria="ruta",
        elemento="Ruta accesible",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito=(
            "La ruta accesible debe ser una faja libre de obstáculos, continua "
            "e ininterrumpida. Ancho libre mínimo: 1,20 m en interior y 1,50 m "
            "en exterior o espacio público."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales=(
            "Paso estrechado por mobiliario, maceteros, desniveles u objetos que "
            "reducen el ancho libre continuo."
        ),
        recomendacion="Despejar y/o ampliar el ancho libre a 1,20 m (interior) o 1,50 m (exterior).",
    ),
    CriterioNormativo(
        id="RUTA_ALTURA_LIBRE",
        categoria="ruta",
        elemento="Altura libre de paso",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito="La altura libre de paso de la ruta accesible debe ser mínimo 2,10 m.",
        discapacidades=["Transversal", "Ceguera"],
        pistas_visuales="Elementos colgantes, vigas o letreros bajos que invaden el paso.",
        recomendacion="Elevar o reubicar el elemento para dejar 2,10 m libres.",
    ),
    CriterioNormativo(
        id="RUTA_PENDIENTE_TRANSVERSAL",
        categoria="ruta",
        elemento="Pendiente transversal",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito="La pendiente transversal de la ruta accesible no debe superar el 2%.",
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Vereda visiblemente inclinada hacia un costado.",
        recomendacion="Corregir la superficie para una pendiente transversal de hasta 2%.",
    ),
    CriterioNormativo(
        id="RUTA_PAVIMENTO",
        categoria="ruta",
        elemento="Pavimento",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito=(
            "Los pavimentos de la ruta accesible deben ser planos, firmes, "
            "estables y antideslizantes, tanto en seco como mojados."
        ),
        discapacidades=["Movilidad reducida", "Personas mayores", "Baja visión"],
        pistas_visuales="Pavimento suelto, irregular, con hoyos, gravilla o piezas faltantes.",
        recomendacion="Reponer o nivelar el pavimento con material firme y antideslizante.",
    ),
    CriterioNormativo(
        id="ACCESO_PRINCIPAL",
        categoria="puerta",
        elemento="Acceso principal",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8",
        requisito=(
            "El acceso principal debe ser parte de la ruta accesible. Se prohíbe "
            "resolver la accesibilidad por accesos secundarios o de servicio."
        ),
        discapacidades=["Transversal"],
        pistas_visuales="Acceso principal con escalones y rampa derivada a una entrada lateral o de servicio.",
        recomendacion="Hacer accesible el acceso principal, no derivar a entradas secundarias.",
    ),
    CriterioNormativo(
        id="PUERTA_ANCHO",
        categoria="puerta",
        elemento="Puerta",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito=(
            "Ancho libre de puerta mínimo 90 cm con la hoja abierta a 90°. "
            "La reducción a 80 cm solo se admite en interiores de viviendas adaptadas."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Puerta angosta; vano que no permite el paso de una silla de ruedas.",
        recomendacion="Ampliar el vano para un ancho libre de 90 cm.",
    ),
    CriterioNormativo(
        id="PUERTA_MANILLA",
        categoria="puerta",
        elemento="Mecanismo de apertura",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3271 (DALCO)",
        requisito=(
            "Manillas tipo palanca o de presión, a una altura entre 0,90 m y 1,20 m. "
            "Se prohíben los pomos redondos."
        ),
        discapacidades=["Movilidad reducida", "Destreza manual reducida"],
        pistas_visuales="Pomo redondo o manilla fuera del rango de altura.",
        recomendacion="Reemplazar por manilla tipo palanca a 0,90–1,20 m.",
    ),
    CriterioNormativo(
        id="PUERTA_ZOCALO",
        categoria="puerta",
        elemento="Zócalo de protección",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito="Las puertas deben tener protección de alto impacto en los 30 cm inferiores.",
        discapacidades=["Usuarios de silla de ruedas"],
        pistas_visuales="Puerta sin zócalo de protección inferior.",
        recomendacion="Instalar zócalo de protección en los 30 cm inferiores.",
    ),
    CriterioNormativo(
        id="PASILLO_GIRO",
        categoria="ruta",
        elemento="Pasillo / Área de giro",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito=(
            "Ancho mínimo de pasillo 90 cm. En fondos de saco (sin salida) se "
            "exige un área de giro libre de obstáculos de 1,50 m de diámetro."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Pasillo estrecho o pasillo ciego sin espacio para girar.",
        recomendacion="Garantizar 90 cm de ancho y un área de giro de 1,50 m de diámetro en fondos de saco.",
    ),
    CriterioNormativo(
        id="DESNIVEL_UMBRAL",
        categoria="ruta",
        elemento="Desnivel / Umbral",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito="Los desniveles en la ruta no pueden superar 2 cm sin solución de rampa.",
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Escalón o umbral de acceso sin rampa que lo salve.",
        recomendacion="Eliminar el desnivel o cubrir con rampa de pendiente adecuada.",
    ),
    CriterioNormativo(
        id="RAMPA_PENDIENTE",
        categoria="rampa",
        elemento="Rampa",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito=(
            "Pendiente máxima según el largo del tramo (L): para L hasta 1,5 m, "
            "máx. 12%; para L entre 1,5 m y 9 m, pendiente decreciente según la "
            "fórmula i% = 12,8 - 0,5333·L, llegando hasta 8%."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Rampa visiblemente muy inclinada para su longitud.",
        recomendacion="Ajustar la pendiente al máximo según largo, extendiendo el desarrollo de la rampa.",
    ),
    CriterioNormativo(
        id="RAMPA_DESCANSO",
        categoria="rampa",
        elemento="Descanso de rampa",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito=(
            "Descansos obligatorios cada 9 m de desarrollo horizontal, planos y "
            "con longitud mínima de 1,50 m."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Rampa larga continua sin descansos intermedios.",
        recomendacion="Incorporar descansos planos de 1,50 m cada 9 m de desarrollo.",
    ),
    CriterioNormativo(
        id="RAMPA_PASAMANOS",
        categoria="rampa",
        elemento="Pasamanos",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito=(
            "Pasamanos continuos a ambos lados, instalados a doble altura "
            "(95 cm y 75 cm)."
        ),
        discapacidades=["Movilidad reducida", "Personas mayores", "Baja visión"],
        pistas_visuales="Ausencia de pasamanos, pasamanos en un solo lado o a una sola altura.",
        recomendacion="Instalar pasamanos continuos a ambos lados, a doble altura (95 y 75 cm).",
    ),
    CriterioNormativo(
        id="REBAJE_SOLERA",
        categoria="ruta",
        elemento="Rebaje de solera",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito=(
            "En cruces o encuentros de calzada, el resalto vertical máximo "
            "permitido del rebaje de solera es de 8 mm."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Baja visión"],
        pistas_visuales="Esquina o cruce sin rebaje, o con resalto/escalón marcado.",
        recomendacion="Ejecutar rebaje de solera con resalto máximo de 8 mm.",
    ),
    CriterioNormativo(
        id="ASCENSOR_CABINA",
        categoria="ascensor",
        elemento="Cabina de ascensor",
        norma="OGUC (DS 50)",
        articulo="NCh 3269",
        requisito=(
            "Cabina mínima estándar 1,10 m de ancho x 1,40 m de fondo; en alta "
            "concurrencia 1,30 m x 1,60 m."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Cabina notoriamente pequeña para una silla de ruedas.",
        recomendacion="Adecuar la cabina a las dimensiones mínimas según uso.",
    ),
    CriterioNormativo(
        id="ASCENSOR_INTERFAZ",
        categoria="ascensor",
        elemento="Botonera e interfaz de ascensor",
        norma="OGUC (DS 50)",
        articulo="NCh 3269 · NCh 3271 (DALCO)",
        requisito=(
            "Botoneras con macrocaracteres en altorrelieve y sistema Braille, más "
            "audio audible que indique piso y dirección de marcha."
        ),
        discapacidades=["Ceguera", "Baja visión"],
        pistas_visuales="Botonera sin Braille ni altorrelieve.",
        recomendacion="Instalar botonera con altorrelieve, Braille y sistema de audio.",
    ),
    CriterioNormativo(
        id="BANO_GIRO",
        categoria="bano",
        elemento="Servicio higiénico accesible (giro)",
        norma="OGUC (DS 50)",
        articulo="Art. 4.1.7 y 4.1.9",
        requisito=(
            "Espacio libre interior que permita inscribir un círculo de 1,50 m "
            "de diámetro, libre del barrido de la puerta y de los artefactos."
        ),
        discapacidades=["Usuarios de silla de ruedas"],
        pistas_visuales="Baño estrecho donde una silla de ruedas no podría girar.",
        recomendacion="Reorganizar el recinto para un giro libre de 1,50 m de diámetro.",
    ),
    CriterioNormativo(
        id="BANO_PUERTA",
        categoria="bano",
        elemento="Puerta de baño accesible",
        norma="OGUC (DS 50)",
        articulo="Art. 4.1.7 y 4.1.9",
        requisito=(
            "Apertura hacia el exterior o sistema corredera, con cerradura "
            "exterior destrabable en caso de emergencia."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Puerta de baño que abre hacia adentro.",
        recomendacion="Cambiar la apertura hacia el exterior o a corredera, con cerradura de emergencia.",
    ),
    CriterioNormativo(
        id="BANO_INODORO",
        categoria="bano",
        elemento="Inodoro y transferencia",
        norma="OGUC (DS 50)",
        articulo="Art. 4.1.7 y 4.1.9",
        requisito=(
            "Altura de taza entre 46 cm y 48 cm, con espacio lateral de "
            "transferencia libre de 80 x 120 cm."
        ),
        discapacidades=["Usuarios de silla de ruedas"],
        pistas_visuales="Inodoro sin espacio lateral de transferencia.",
        recomendacion="Reubicar el artefacto dejando 80 x 120 cm de transferencia lateral.",
    ),
    CriterioNormativo(
        id="BANO_BARRAS",
        categoria="bano",
        elemento="Barras de apoyo",
        norma="OGUC (DS 50)",
        articulo="Art. 4.1.7 y 4.1.9",
        requisito=(
            "Barras de diámetro 3 a 4 cm, separadas 4,5 cm del muro, resistentes "
            "a 100 kg de tracción: una fija y una abatible al costado de transferencia."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Ausencia de barras de apoyo junto al inodoro.",
        recomendacion="Instalar barra fija y barra abatible al costado de transferencia.",
    ),
    CriterioNormativo(
        id="BANO_LAVAMANOS",
        categoria="bano",
        elemento="Lavamanos",
        norma="OGUC (DS 50)",
        articulo="Art. 4.1.7 y 4.1.9",
        requisito=(
            "Lavamanos suspendido (sin pedestal ni mueble), con altura libre "
            "inferior mínima de 70 cm y grifería tipo palanca o sensor."
        ),
        discapacidades=["Usuarios de silla de ruedas"],
        pistas_visuales="Lavamanos con pedestal o mueble que impide acercar la silla.",
        recomendacion="Instalar lavamanos suspendido con 70 cm libres y grifería de palanca o sensor.",
    ),
    CriterioNormativo(
        id="BANO_ESPEJO",
        categoria="bano",
        elemento="Espejo",
        norma="OGUC (DS 50)",
        articulo="Art. 4.1.7 y 4.1.9",
        requisito="Borde inferior del espejo a altura máxima de 90 cm, o espejo inclinado a 10°.",
        discapacidades=["Usuarios de silla de ruedas"],
        pistas_visuales="Espejo alto, no utilizable desde una silla de ruedas.",
        recomendacion="Bajar el borde inferior a 90 cm o inclinar el espejo a 10°.",
    ),
    CriterioNormativo(
        id="BANO_PANICO",
        categoria="emergencia",
        elemento="Botón de pánico en baño",
        norma="OGUC (DS 50)",
        articulo="Art. 4.1.7 y 4.1.9",
        requisito=(
            "Pulsador o tirador a ras de suelo, conectado a luz estroboscópica y "
            "señal acústica exterior sobre la puerta del baño."
        ),
        discapacidades=["Transversal"],
        pistas_visuales="Baño accesible sin sistema de alarma de emergencia.",
        recomendacion="Instalar botón de pánico a ras de suelo con señal lumínica y acústica exterior.",
    ),
    CriterioNormativo(
        id="ESTAC_DIMENSION",
        categoria="estacionamiento",
        elemento="Estacionamiento reservado",
        norma="OGUC (DS 50)",
        articulo="Art. 2.4.2",
        requisito=(
            "Mínimo 2,50 m de ancho más una franja de circulación segura adosada "
            "de 1,10 m (módulo total 3,60 m), ubicado inmediato a los accesos "
            "peatonales de la ruta accesible."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Estacionamiento estrecho o sin franja de transferencia.",
        recomendacion="Demarcar módulo de 3,60 m (2,50 m + franja 1,10 m) junto al acceso.",
    ),
    CriterioNormativo(
        id="ESTAC_SIA",
        categoria="estacionamiento",
        elemento="Señalización SIA",
        norma="OGUC (DS 50)",
        articulo="Art. 2.4.2 · NCh 3180 (SIA)",
        requisito=(
            "Símbolo Internacional de Accesibilidad (SIA) pintado en el pavimento "
            "(blanco sobre azul Pantone 294C) más señalética vertical."
        ),
        discapacidades=["Transversal"],
        pistas_visuales="Estacionamiento sin SIA en pavimento o sin señal vertical.",
        recomendacion="Pintar el SIA en el pavimento e instalar señalética vertical.",
    ),
    CriterioNormativo(
        id="MESON_ATENCION",
        categoria="mobiliario",
        elemento="Mesón de atención / caja",
        norma="OGUC (DS 50)",
        articulo="NCh 3269 · NCh 3271 (DALCO)",
        requisito=(
            "Sección rebajada de mínimo 80 cm de ancho, altura máxima 80 cm y "
            "despeje inferior para rodillas de 70 cm."
        ),
        discapacidades=["Usuarios de silla de ruedas"],
        pistas_visuales="Mesón alto y continuo sin sección rebajada.",
        recomendacion="Habilitar un tramo de mesón rebajado a 80 cm con despeje inferior de 70 cm.",
    ),
    CriterioNormativo(
        id="MOBILIARIO_ALTURA_OPERATIVA",
        categoria="mobiliario",
        elemento="Tótem / cajero / interruptor",
        norma="OGUC (DS 50)",
        articulo="NCh 3269 · NCh 3271 (DALCO)",
        requisito=(
            "Componentes operativos a altura entre 90 cm y 1,20 m; enchufes a "
            "altura mínima de 40 cm."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Cajero, tótem o interruptor fuera del rango de alcance.",
        recomendacion="Reubicar los componentes operativos a 90–120 cm de altura.",
    ),
    CriterioNormativo(
        id="PODOTACTIL",
        categoria="sensorial",
        elemento="Señalización podotáctil",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito=(
            "Baldosas de guía (líneas) y de alerta (botones / conos truncados) "
            "obligatorias antes de escaleras, rampas, andenes, desniveles y "
            "cruces peatonales."
        ),
        discapacidades=["Ceguera", "Baja visión"],
        pistas_visuales="Escalera, cruce o desnivel sin pavimento podotáctil de alerta.",
        recomendacion="Instalar baldosas podotáctiles de guía y de alerta donde la ruta lo exige.",
    ),
    CriterioNormativo(
        id="PROTECCION_ALTURA_LIBRE",
        categoria="sensorial",
        elemento="Protección bajo elementos a baja altura",
        norma="OGUC (DS 50)",
        articulo="Art. 2.2.8 · NCh 3269",
        requisito=(
            "Todo elemento suspendido o diagonal de escalera con altura inferior "
            "a 2,10 m debe bloquearse físicamente en el suelo (jardinera o "
            "barrera) para evitar impactos craneales a personas ciegas."
        ),
        discapacidades=["Ceguera", "Baja visión"],
        pistas_visuales="Bajo-escalera o elemento colgante a baja altura sin barrera al piso.",
        recomendacion="Bloquear físicamente al suelo el área bajo el elemento a baja altura.",
    ),
    CriterioNormativo(
        id="ZONA_REFUGIO",
        categoria="emergencia",
        elemento="Zona de refugio en escalera",
        norma="OGUC (DS 50)",
        articulo="NCh 3269 (evacuación inclusiva)",
        requisito=(
            "A partir del segundo piso, las cajas de escaleras presurizadas deben "
            "incluir un espacio plano demarcado de 80 x 120 cm para una silla de "
            "ruedas, con intercomunicador bidireccional accesible a conserjería."
        ),
        discapacidades=["Usuarios de silla de ruedas", "Movilidad reducida"],
        pistas_visuales="Escalera de evacuación sin espacio demarcado de refugio.",
        recomendacion="Demarcar zona de refugio de 80 x 120 cm con intercomunicador.",
    ),
    CriterioNormativo(
        id="ALARMA_MIXTA",
        categoria="emergencia",
        elemento="Alarma de emergencia mixta",
        norma="OGUC (DS 50)",
        articulo="NCh 3269 (evacuación inclusiva)",
        requisito=(
            "Dispositivos mixtos obligatorios: señal acústica (sirena) sincronizada "
            "con señal lumínica estroboscópica en todos los recintos, incluidos "
            "pasillos y baños."
        ),
        discapacidades=["Sordera", "Hipoacusia", "Ceguera"],
        pistas_visuales="Alarma solo sonora (sin baliza lumínica) o solo lumínica.",
        recomendacion="Instalar alarmas mixtas (acústica + lumínica estroboscópica) en todos los recintos.",
    ),
    CriterioNormativo(
        id="WAYFINDING",
        categoria="sensorial",
        elemento="Señalética cognitiva (wayfinding)",
        norma="OGUC (DS 50)",
        articulo="NCh 3271 (DALCO)",
        requisito=(
            "Señalética mediante pictogramas universales simplificados de alto "
            "contraste cromático para evitar la desorientación."
        ),
        discapacidades=["Discapacidad cognitiva", "Baja visión"],
        pistas_visuales="Señalética solo textual, ambigua o de bajo contraste.",
        recomendacion="Incorporar pictogramas universales de alto contraste.",
    ),
]


def catalogo_para_prompt() -> str:
    lineas = []
    for c in CATALOGO:
        lineas.append(
            f"- id: {c.id}\n"
            f"  categoria: {c.categoria}\n"
            f"  elemento: {c.elemento}\n"
            f"  norma: {c.norma}\n"
            f"  articulo: {c.articulo}\n"
            f"  requisito: {c.requisito}\n"
            f"  discapacidades: {', '.join(c.discapacidades)}\n"
            f"  recomendacion_tipo: {c.recomendacion}"
        )
    return "\n".join(lineas)


def buscar_criterio(criterio_id: str) -> "CriterioNormativo | None":
    for c in CATALOGO:
        if c.id == criterio_id:
            return c
    return None


ENTORNOS = {
    "Parque": {"ruta", "rampa", "sensorial", "mobiliario", "estacionamiento"},
    "Plaza": {"ruta", "rampa", "sensorial", "mobiliario", "estacionamiento"},
    "Vereda / Acera": {"ruta", "rampa", "sensorial"},
    "Edificio de uso público": {"ruta", "puerta", "rampa", "ascensor", "bano",
                                "estacionamiento", "mobiliario", "sensorial", "emergencia"},
    "Mobiliario urbano": {"mobiliario", "sensorial", "ruta"},
}


def criterios_por_entorno(entorno: str) -> "list[CriterioNormativo]":
    cats = ENTORNOS.get(entorno)
    if not cats:
        return list(CATALOGO)
    return [c for c in CATALOGO if c.categoria in cats]
