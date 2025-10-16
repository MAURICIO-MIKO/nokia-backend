from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from main import main  # Tu función que procesa Excel → XML

app = FastAPI()

# 🔓 Permitir llamadas desde tu nuevo frontend en GitHub Pages
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

@app.get("/")
def home():
    return {"status": "✅ API Nokia lista y funcionando correctamente"}

@app.post("/procesar")
async def procesar(excel: UploadFile, plantilla: str = Form(...)):
    """
    Recibe un Excel y una plantilla XML, genera salida.xml y devuelve el archivo.
    """
    try:
        # 📁 Guardar Excel recibido en carpeta persistente
        tmp_dir = "/tmp"
        os.makedirs(tmp_dir, exist_ok=True)

        excel_path = os.path.join(tmp_dir, excel.filename)
        with open(excel_path, "wb") as f:
            f.write(await excel.read())

        # 🧠 Ejecutar tu función principal (genera salida.xml)
        main(excel_path, plantilla)

        # 📄 Verificar que salida.xml existe
        salida_local = "salida.xml"
        salida_final = os.path.join(tmp_dir, "salida.xml")

        if not os.path.exists(salida_local):
            return JSONResponse(status_code=500, content={"error": "❌ No se generó salida.xml correctamente."})

        # Copiar el archivo a /tmp (sin borrar el original)
        os.replace(salida_local, salida_final)
        print(f"✅ XML final listo en {salida_final}")

        # 📦 Devolver el archivo al cliente
        return FileResponse(
            salida_final,
            media_type="application/xml",
            filename="salida.xml"
        )

    except Exception as e:
        print(f"❌ Error interno: {e}")
        return JSONResponse(status_code=500, content={"error": f"Error procesando XML: {str(e)}"})
