from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import xml.etree.ElementTree as ET
from xml.dom import minidom
import tempfile
import os

# Importaciones existentes
from main import main as main_general
from solo_5G_main import main as main_5g

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # GitHub Pages y cualquier dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "API funcionando correctamente"}

# ======================================================
# NUEVO ENDPOINT: borrar ID de WNCELG correctamente
# ======================================================
@app.post("/borrarWNCELG")
async def borrar_wncelg(xml_file: UploadFile = File(...), wncel_id: str = Form(...)):
    """
    Borra el <p> cuyo contenido coincide con wncel_id dentro de <list name="wncelIdList">
    en un bloque WNCELG. Si la lista queda vacía, borra también ese WNCELG.
    """

    try:
        # Guardar archivo temporal
        temp_path = tempfile.mktemp(suffix=".xml")
        with open(temp_path, "wb") as f:
            f.write(await xml_file.read())

        tree = ET.parse(temp_path)
        root = tree.getroot()

        cambios = False
        eliminar_mos = []  # Para marcar los bloques a borrar

        # Buscar todos los WNCELG
        for mo in root.findall(".//managedObject[@class='com.nokia.srbts.wcdma:WNCELG']"):

            lista = mo.find(".//list[@name='wncelIdList']")
            if lista is None:
                continue

            # Eliminar el ID específico
            for p in lista.findall("p"):
                if p.text.strip() == wncel_id:
                    lista.remove(p)
                    cambios = True

            # Si ya no quedan entradas → borrar el bloque entero
            if len(lista.findall("p")) == 0:
                eliminar_mos.append(mo)
                cambios = True

        # Eliminar managedObjects marcados
        for mo in eliminar_mos:
            root.remove(mo)

        if not cambios:
            return JSONResponse(
                {"error": f"No se encontró el ID {wncel_id} en ningún WNCELG"},
                status_code=404
            )

        # Guardar XML bonito SIN romper estructura Nokia
        output_file = tempfile.mktemp(prefix="XML_mod_", suffix=".xml")
        rough = ET.tostring(root, encoding="utf-8")

        reparsed = minidom.parseString(rough)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        return FileResponse(
            output_file,
            media_type="application/xml",
            filename=f"XML_sin_{wncel_id}.xml"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
