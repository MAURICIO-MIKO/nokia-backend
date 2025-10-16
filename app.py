from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import shutil
from main import main  # función que procesa Excel → XML

app = FastAPI()

# 🔓 Permitir llamadas desde tu frontend de GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cirecet-optimizacion-web-nokia.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API Nokia lista ✅"}

@app.post("/procesar")
async def procesar(excel: UploadFile, plantilla: str = Form(...)):
    # Crear carpeta temporal
    with tempfile.TemporaryDirectory() as tmp:
        excel_path = os.path.join(tmp, excel.filename)
        with open(excel_path, "wb") as f:
            f.write(await excel.read())

        # Llamar a tu función principal
        main(excel_path, plantilla)

        # Copiar salida.xml al directorio temporal
        salida_path = os.path.join(tmp, "salida.xml")
        if os.path.exists("salida.xml"):
            shutil.copy("salida.xml", salida_path)
        else:
            return {"error": "No se generó salida.xml"}

        return FileResponse(
            salida_path,
            media_type="application/xml",
            filename="salida.xml"
        )
