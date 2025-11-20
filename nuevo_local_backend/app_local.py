from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from generador_5g_moderno import generar_mr_bts_moderno
import shutil, os, traceback

# ============================================================
# 🚀 Configuración del servidor FastAPI en modo local
# ============================================================

app = FastAPI(
    title="🧠 Nokia Local Backend",
    description="Servidor local para pruebas del generador XML 5G",
    version="1.0-local"
)

# ============================================================
# 🌍 Permitir conexiones desde tu navegador local (CORS)
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Si usas Live Server: ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🏠 Ruta principal de prueba
# ============================================================

@app.get("/")
def home():
    return {"estado": "✅ Servidor local Nokia activo y listo para recibir Excel"}

# ============================================================
# 📤 Endpoint principal: generar XML 5G
# ============================================================

@app.post("/generar-xml-5g")
async def generar_xml_5g(excel: UploadFile):
    """
    Recibe un archivo Excel (.xlsx) con hoja '5G' y devuelve el XML generado.
    Usa la plantilla plantilla_5g.xml en el mismo directorio.
    """
    try:
        # 1️⃣ Crear carpeta temporal (local, compatible con Windows)
        temp_dir = os.path.join(os.getcwd(), "tmp")
        os.makedirs(temp_dir, exist_ok=True)

        # 2️⃣ Guardar el Excel subido en esa carpeta
        temp_excel = os.path.join(temp_dir, excel.filename)
        with open(temp_excel, "wb") as f:
            shutil.copyfileobj(excel.file, f)

        if not os.path.exists(temp_excel):
            raise FileNotFoundError(f"No se pudo guardar el archivo: {temp_excel}")

        # 3️⃣ Buscar la plantilla XML en el mismo directorio
        plantilla = os.path.join(os.path.dirname(__file__), "plantilla_5g.xml")
        if not os.path.exists(plantilla):
            raise FileNotFoundError(f"No se encontró la plantilla XML: {plantilla}")

        # 4️⃣ Generar XML usando la lógica en generador_5g_moderno.py
        salida = generar_mr_bts_moderno(plantilla, temp_excel)

        # 5️⃣ Enviar el archivo XML resultante al navegador
        return FileResponse(
            salida,
            filename=os.path.basename(salida),
            media_type="application/xml"
        )

    # ========================================================
    # 🚨 Manejo de errores detallado
    # ========================================================
    except Exception as e:
        print("\n=== ERROR DETECTADO ===")
        traceback.print_exc()
        print("=======================\n")
        return JSONResponse(status_code=500, content={"error": str(e)})
