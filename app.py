from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

# 🧠 Importamos los dos scripts distintos
from main import main as main_general
from solo_5G_main import main as main_5g

app = FastAPI()

# 🔓 Permitir llamadas desde tu frontend en GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mauricio-miko.github.io",
        "https://mauricio-miko.github.io/Cirecet-web-optimizacion-nokia-v2.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🏠 Ruta de prueba
@app.get("/")
def home():
    return {"status": "✅ API Nokia lista y funcionando correctamente"}


# 🧩 1️⃣ Endpoint que usa main.py (el general)
@app.post("/procesar")
async def procesar(excel: UploadFile, plantilla: str = Form(...)):
    """
    Recibe un Excel y una plantilla XML, genera salida.xml usando main.py
    """
    return await procesar_generico(excel, plantilla, main_general, "main.py")


# 🧩 2️⃣ Endpoint que usa solo_5G_main.py
@app.post("/procesar5G")
async def procesar_5g(excel: UploadFile, plantilla: str = Form(...)):
    """
    Recibe un Excel y una plantilla XML, genera salida.xml usando solo_5G_main.py
    """
    return await procesar_generico(excel, plantilla, main_5g, "solo_5G_main.py")


# 🧠 Función auxiliar que evita repetir código
async def procesar_generico(excel, plantilla, funcion_main, origen):
    try:
        # 📁 Carpeta temporal segura
        tmp_dir = "/tmp"
        os.makedirs(tmp_dir, exist_ok=True)

        # 📥 Guardar el Excel
        excel_path = os.path.join(tmp_dir, excel.filename)
        with open(excel_path, "wb") as f:
            f.write(await excel.read())

        print(f"🧩 Ejecutando {origen} para generar XML...")
        funcion_main(excel_path, plantilla)  # Ejecuta la función pasada (main o main_5G)

        # 📄 Archivo generado localmente
        salida_local = "salida.xml"
        salida_tmp = os.path.join(tmp_dir, "salida.xml")

        if not os.path.exists(salida_local):
            return JSONResponse(
                status_code=500,
                content={"error": f"❌ No se generó salida.xml correctamente desde {origen}."}
            )

        shutil.copy(salida_local, salida_tmp)
        print(f"✅ XML copiado en {salida_tmp}")

        # 📦 Devolver al cliente
        return FileResponse(
            salida_tmp,
            media_type="application/xml",
            filename="salida.xml"
        )

    except Exception as e:
        print(f"❌ Error interno ({origen}): {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error procesando XML desde {origen}: {str(e)}"}
        )
