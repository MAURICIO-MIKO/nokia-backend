from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from main import main  # Tu función que procesa Excel → XML

app = FastAPI()

# 🔓 Permitir llamadas desde tu nuevo frontend en GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mauricio-miko.github.io", 
                   "https://mauricio-miko.github.io/Cirecet-web-optimizacion-nokia-v2.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "✅ API Nokia lista y funcionando correctamente"}

@app.post("/procesar")
async def procesar(excel: UploadFile, plantilla: str = Form(...)):
    """
    Recibe un Excel y una plantilla XML, genera salida.xml y devuelve el archivo.
    """
    # 📁 Carpeta temporal persistente (Render no borra /tmp automáticamente)
    tmp_dir = "/tmp"
    os.makedirs(tmp_dir, exist_ok=True)

    # 📥 Guardar Excel recibido
    excel_path = os.path.join(tmp_dir, excel.filename)
    with open(excel_path, "wb") as f:
        f.write(await excel.read())

    # 🧠 Ejecutar procesamiento
    main(excel_path, plantilla)

    # 📤 Copiar salida.xml a carpeta temporal
    salida_local = "salida.xml"
    salida_path = os.path.join(tmp_dir, "salida.xml")

    if os.path.exists(salida_local):
        shutil.copy(salida_local, salida_path)
    else:
        return {"error": "❌ No se generó salida.xml correctamente."}

    print(f"✅ Archivo XML generado en {salida_path}")

    # 📦 Enviar el archivo al cliente
    return FileResponse(
        salida_path,
        media_type="application/xml",
        filename="salida.xml"
    )
