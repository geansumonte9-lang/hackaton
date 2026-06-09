import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODELO_IA = os.getenv("MODELO_IA", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

RAIZ = Path(__file__).parent
CARPETA_SALIDA = RAIZ / "informes"
CARPETA_SALIDA.mkdir(exist_ok=True)

CARPETA_FOTOS = RAIZ / "fotos"
CARPETA_FOTOS.mkdir(exist_ok=True)

CARPETA_SCANAPP = RAIZ / "scanapp_fotos"
CARPETA_SCANAPP.mkdir(exist_ok=True)

CARPETA_EVIDENCIAS = RAIZ / "evidencias"
CARPETA_EVIDENCIAS.mkdir(exist_ok=True)

CONFIANZA_MINIMA = 0.25

ORGANIZACION = "Plataforma Ciudadana de Auditoría de Accesibilidad"
