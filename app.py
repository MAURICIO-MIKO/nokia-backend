from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from main import main

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://Cirecet-optimizacion-web-nokia.github.io"],  # tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API Nokia lista ✅"}

@app.post("/procesar")
async def procesar(excel: UploadFile, plantilla: str = Form(...)):
    with tempfile.TemporaryDirectory() as tmp:
        excel_path = os.path.join(tmp, excel.filename)
        with open(excel_path, "wb") as f:
            f.write(await excel.read())

        # Ruta absoluta de plantilla
        plantilla_path = os.path.join(os.path.dirname(__file__), plantilla)
        salida_path = os.path.join(tmp, "salida.xml")

        main(excel_path, plantilla_path)

        # Copiar el archivo de salida al temp si tu main lo guarda en el directorio raíz
        if not os.path.exists(salida_path) and os.path.exists("salida.xml"):
            os.rename("salida.xml", salida_path)

        # 🔹 Devolver el archivo directamente al frontend
        return FileResponse(
            salida_path,
            media_type="application/xml",
            filename="salida.xml"
        )
