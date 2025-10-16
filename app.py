from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from main import main  # Tu función que procesa Excel → XML

app = FastAPI()

# 🔓 Permitir llamadas desde tu GitHub Pages:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://Cirecet-optimizacion-web-nokia.github.io"],
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

        # Llama a tu función principal
        main(excel_path, plantilla)

        salida = "salida.xml"
        return FileResponse(
            salida,
            media_type="application/xml",
            filename="salida.xml"
        )
