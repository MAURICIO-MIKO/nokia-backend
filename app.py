from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import xml.etree.ElementTree as ET
import mammoth
from xml.dom import minidom

# ==============================
# Importaciones existentes
# ==============================
from main import main as main_general
from solo_5G_main import main as main_5g

app = FastAPI()

# 🔓 Permitir llamadas desde GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mauricio-miko.github.io",
        "https://mauricio-miko.github.io/Cirecet-web-optimizacion-nokia-v2.github.io",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================================================
# 🏠 Ruta de prueba
# =======================================================
@app.get("/")
def home():
    return {"status": "✅ API Nokia lista y funcionando correctamente"}

# =======================================================
# 1️⃣ Endpoint que usa main.py (general)
# =======================================================
@app.post("/procesar")
async def procesar(excel: UploadFile, plantilla: str = Form(...)):
    return await procesar_generico(excel, plantilla, main_general, "main.py")

# =======================================================
# 2️⃣ Endpoint que usa solo_5G_main.py
# =======================================================
@app.post("/procesar5G")
async def procesar_5g(excel: UploadFile, plantilla: str = Form(...)):
    return await procesar_generico(excel, plantilla, main_5g, "solo_5G_main.py")

# =======================================================
# 🔧 Función auxiliar (SE MANTIENE COMO ESTABA)
# =======================================================
async def procesar_generico(excel, plantilla, funcion_main, origen):
    try:
        tmp_dir = "/tmp"
        os.makedirs(tmp_dir, exist_ok=True)

        excel_path = os.path.join(tmp_dir, excel.filename)
        with open(excel_path, "wb") as f:
            f.write(await excel.read())

        xml_generado = funcion_main(excel_path, plantilla)

        if not os.path.exists(xml_generado):
            return JSONResponse(
                status_code=500,
                content={"error": f"❌ No se generó el archivo desde {origen}"}
            )

        return FileResponse(
            xml_generado,
            media_type="application/xml",
            filename=os.path.basename(xml_generado)
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error interno en {origen}: {str(e)}"}
        )

# =======================================================
# 3️⃣ Convertir manual Word → HTML (SE MANTIENE)
# =======================================================
@app.post("/convertirWordManual")
async def convertir_word_manual(archivo: UploadFile):
    try:
        if not archivo.filename.endswith(".docx"):
            return JSONResponse(
                status_code=400,
                content={"error": "Solo se permiten archivos .docx"}
            )

        tmp_path = f"/tmp/{archivo.filename}"
        with open(tmp_path, "wb") as f:
            f.write(await archivo.read())

        with open(tmp_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value

        return {"html": html_content}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error convirtiendo Word: {str(e)}"}
        )


# =======================================================
# ⭐ 4️⃣ NUEVO ENDPOINT — BORRAR WNCELG
#   (VERSIÓN FINAL, ÚNICA, FUNCIONAL)
# =======================================================
@app.post("/borrarSector3G")
async def borrar_sector_3g(xml_file: UploadFile = File(...), sector: int = Form(...)):

    print("======== DEBUG ========")
    print("xml_file filename:", xml_file.filename if xml_file else "None")
    print("sector recibido:", sector)
    print("========================")

    
    """
    Borra el <p> N dentro de wncelIdList según sector.
    sector = 1 → primer p
    sector = 2 → segundo p
    sector = 3 → tercer p
    """

    try:
        # Guardar archivo temporal
        temp_path = tempfile.mktemp(suffix=".xml")
        with open(temp_path, "wb") as f:
            f.write(await xml_file.read())

        tree = ET.parse(temp_path)
        root = tree.getroot()

        cambios = False
        eliminar_mos = []

        # Buscar bloques WNCELG
        for mo in root.findall(".//managedObject[@class='com.nokia.srbts.wcdma:WNCELG']"):

            lista = mo.find(".//list[@name='wncelIdList']")
            if lista is None:
                continue

            p_list = lista.findall("p")

            # ❌ Si el sector NO existe
            if sector < 1 or sector > len(p_list):
                return JSONResponse(
                    {"error": f"❌ La celda 3G del sector {sector} no existe."},
                    status_code=404
                )

            # Convertir sector → índice de lista
            index = sector - 1

            # Borrar el <p> correspondiente
            lista.remove(p_list[index])
            cambios = True

            # Si la lista queda vacía → borrar el bloque completo
            if len(lista.findall("p")) == 0:
                eliminar_mos.append(mo)

        # Eliminar bloques completos
        for mo in eliminar_mos:
            root.remove(mo)

        if not cambios:
            return JSONResponse(
                {"error": "❌ No se aplicaron cambios."},
                status_code=400
            )

        # Guardar XML modificado
        output_file = tempfile.mktemp(prefix="XML_mod_", suffix=".xml")
        rough = ET.tostring(root, encoding="utf-8")
        pretty_xml = minidom.parseString(rough).toprettyxml(indent="  ")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        return FileResponse(
            output_file,
            media_type="application/xml",
            filename=f"XML_sector{sector}_3G_eliminado.xml"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

