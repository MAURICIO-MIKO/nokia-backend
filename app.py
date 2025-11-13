from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import mammoth  # 🧠 Para convertir Word a HTML

# 🧩 Importamos los dos scripts principales
from main import main as main_general
from solo_5G_main import main as main_5g

app = FastAPI()

# 🔓 Permitir llamadas desde el frontend en GitHub Pages
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

# 🧩 1️⃣ Endpoint que usa main.py (general)
@app.post("/procesar")
async def procesar(excel: UploadFile, plantilla: str = Form(...)):
    """Recibe un Excel y una plantilla XML, genera salida.xml usando main.py"""
    return await procesar_generico(excel, plantilla, main_general, "main.py")

# 🧩 2️⃣ Endpoint que usa solo_5G_main.py
@app.post("/procesar5G")
async def procesar_5g(excel: UploadFile, plantilla: str = Form(...)):
    """Recibe un Excel y una plantilla XML, genera salida.xml usando solo_5G_main.py"""
    return await procesar_generico(excel, plantilla, main_5g, "solo_5G_main.py")

# 🧠 Función auxiliar que evita repetir código
async def procesar_generico(excel, plantilla, funcion_main, origen):
    try:
        tmp_dir = "/tmp"
        os.makedirs(tmp_dir, exist_ok=True)

        # 📥 Guardar el Excel temporalmente
        excel_path = os.path.join(tmp_dir, excel.filename)
        with open(excel_path, "wb") as f:
            f.write(await excel.read())

        print(f"🧩 Ejecutando {origen} para generar XML...")

        # Ejecutar función principal
        xml_generado = funcion_main(excel_path, plantilla)

        if not os.path.exists(xml_generado):
            return JSONResponse(
                status_code=500,
                content={"error": f"❌ No se generó el archivo correctamente desde {origen}."}
            )

        print(f"✅ XML generado en {xml_generado}")

        return FileResponse(
            xml_generado,
            media_type="application/xml",
            filename=os.path.basename(xml_generado)
        )

    except Exception as e:
        print(f"❌ Error interno ({origen}): {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error procesando XML desde {origen}: {str(e)}"}
        )

# 🧩 3️⃣ Endpoint para convertir Word a HTML
@app.post("/convertirWordManual")
async def convertir_word_manual(archivo: UploadFile):
    """
    Convierte un archivo Word (.docx) a HTML para mostrarlo en el manual de usuario.
    """
    try:
        if not archivo.filename.endswith(".docx"):
            return JSONResponse(
                status_code=400,
                content={"error": "Solo se permiten archivos .docx"}
            )

        # 📁 Guardar temporalmente el archivo subido
        tmp_path = f"/tmp/{archivo.filename}"
        with open(tmp_path, "wb") as f:
            f.write(await archivo.read())

        # 🔄 Convertir a HTML
        with open(tmp_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value

        print(f"✅ Archivo {archivo.filename} convertido correctamente a HTML.")
        return {"html": html_content}

    except Exception as e:
        print(f"❌ Error al convertir Word: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error convirtiendo Word: {str(e)}"}
        )
