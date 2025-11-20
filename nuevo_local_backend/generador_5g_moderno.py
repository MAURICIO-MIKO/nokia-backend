from jinja2 import Template
import openpyxl as xl
import os
from datetime import datetime

def generar_mr_bts_moderno(plantilla_path: str, excel_path: str) -> str:
    """Genera un XML MRBTS (solo 5G) desde un Excel usando Jinja2."""

    wb = xl.load_workbook(excel_path)
    if "5G" not in wb.sheetnames:
        raise ValueError("❌ La hoja '5G' no existe en el Excel.")
    ws = wb["5G"]

    datos = {
        "mr_bts_id": obtener(ws, "mrBTSId"),
        "mr_bts_name": obtener(ws, "gNodeB NAME")[3:],  # quita 'MNB'
        "fecha": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }

    with open(plantilla_path, "r", encoding="utf-8") as f:
        template = Template(f.read())

    xml_final = template.render(datos)

    # 📁 Guardar archivo en carpeta local tmp/
    output_dir = os.path.join(os.getcwd(), "tmp")
    os.makedirs(output_dir, exist_ok=True)
    salida_path = os.path.join(output_dir, f"salida_5G_{datos['mr_bts_id']}.xml")

    with open(salida_path, "w", encoding="utf-8") as f:
        f.write(xml_final)

    print(f"✅ Archivo generado: {salida_path}")
    return salida_path

def obtener(hoja, nombre):
    """Busca un campo en la fila 1 y devuelve el valor debajo."""
    for celda in hoja[1]:
        if celda.value == nombre:
            return hoja[f"{celda.column_letter}2"].value
    raise KeyError(f"⚠️ No se encontró el campo '{nombre}' en la hoja 5G.")
