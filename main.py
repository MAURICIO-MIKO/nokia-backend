import os
import ipaddress
import pandas as pd
import openpyxl as xl


def main(xls, xml):
    """Procesa un Excel y plantilla XML, genera salida.xml"""
    # Convertir .xls en .xlsx si es necesario
    x = pd.read_excel(xls, sheet_name=None, engine="xlrd")
    xlsx = xls + ".xlsx"

    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        for sheet_name, df in x.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    dic = {}
    wb = xl.load_workbook(xlsx)

    # === RECOGE VARIABLES DE 5G ===
    ws = wb["5G"]
    dic["##site##"] = f'{buscaCelda(ws, "Site NAME").replace(" ", "_")}_{buscaCelda(ws, "Cod. CelSig")}'
    dic["##mr_bts_name##"] = buscaCelda(ws, "gNodeB NAME")[3:]
    dic["##mr_bts_id##"] = buscaCelda(ws, "mrBTSId")
    dic["##gnb_id##"] = buscaCelda(ws, "gNodeB id")
    dic["##ip_gnb_oym##"] = buscaCelda(ws, "O&M gNB IP")
    dic["##mask_gnb_oym##"] = ipaddress.IPv4Network(f"0.0.0.0/{buscaCelda(ws, 'O&M NetMask')}").prefixlen
    dic["##gateway_gnb_oym##"] = buscaCelda(ws, "O&M Gateway")
    dic["##vlan_gnb_oym##"] = buscaCelda(ws, "O&M VLAN")
    dic["##ip_ioms_prim_oym##"] = buscaCelda(ws, "O&M iOMS-prim IP")
    dic["##ip_ioms_sec_oym##"] = buscaCelda(ws, "O&M iOMS-sec IP")
    dic["##ip_netact_oym##"] = buscaCelda(ws, "O&M NetAct Subnet").split("/")[0]
    dic["##mask_netact_oym##"] = buscaCelda(ws, "O&M NetAct Subnet").split("/")[1]
    dic["##ip_pki_oym##"] = buscaCelda(ws, "O&M PKI Server IP")
    dic["##ip_gnb_sync##"] = buscaCelda(ws, "Sync gNB IP")
    dic["##mask_gnb_sync##"] = ipaddress.IPv4Network(f"0.0.0.0/{buscaCelda(ws, 'Sync NetMask')}").prefixlen
    dic["##gateway_sync##"] = buscaCelda(ws, "Sync Gateway")
    dic["##vlan_sync##"] = buscaCelda(ws, "Sync VLAN")
    dic["##ip_top1_sync##"] = buscaCelda(ws, "Sync ToP1 IP")
    dic["##ip_top2_sync##"] = buscaCelda(ws, "Sync ToP2 IP")
    dic["##ip_gnb_s1_outer##"] = buscaCelda(ws, "S1 gNB IP/OUTER IP")
    dic["##mask_s1_x2##"] = ipaddress.IPv4Network(f"0.0.0.0/{buscaCelda(ws, 'S1-X2 NetMask')}").prefixlen
    dic["##gateway_s1_x2##"] = buscaCelda(ws, "S1-X2 Gateway")
    dic["##vlan_s1_x2##"] = buscaCelda(ws, "S1-X2 VLAN")
    dic["##ip_gnb_inner##"] = buscaCelda(ws, "INNER IP")
    dic["##gateway_security##"] = buscaCelda(ws, "Security Gateway IP")
    dic["##tac##"] = buscaCelda(ws, "TAC")

    dic["##AMF_mde1##"] = buscaCelda(ws, "AMF nvpcc-amf01/2/3-mde1").split("/")[0]
    dic["##AMF_mno1##"] = buscaCelda(ws, "AMF nvpcc-amf01/2/3-mno1").split("/")[0]
    dic["##AMF_bep1##"] = buscaCelda(ws, "AMF nvpcc-amf01/2/3-bep1").split("/")[0]
    dic["##AMF_btb1##"] = buscaCelda(ws, "AMF nvpcc-amf01/2/3-btb1").split("/")[0]
    dic["##AMF_mad1##"] = buscaCelda(ws, "AMF nvpcc-amf01/2/3-mad1").split("/")[0]

    dic["##Zero correlation zone config NR3500##"] = buscaCelda(ws, "Zero correlation zone config NR3500")
    dic["##Prach Configuration Index NR3500##"] = buscaCelda(ws, "Prach Configuration Index NR3500")
    dic["##Phys Cell Id NR3500##"] = buscaCelda(ws, "Phys Cell Id NR3500")
    dic["##PRACH root sequence Index NR3500##"] = buscaCelda(ws, "PRACH root sequence Index NR3500")

    # === RECOGE VARIABLES DE 4G ===
    ws = wb["4G"]
    dic["##enb_id##"] = buscaCelda(ws, "eNodeB id")
    dic["##ip_enb_s1_outer##"] = buscaCelda(ws, "S1 eNB IP/OUTER IP")
    dic["##mask_s1##"] = ipaddress.IPv4Network(f"0.0.0.0/{buscaCelda(ws, 'S1 NetMask')}").prefixlen
    dic["##gateway_s1_x2##"] = buscaCelda(ws, "S1 Gateway")
    dic["##vlan_s1_x2##"] = buscaCelda(ws, "S1 VLAN")
    dic["##ip_enb_inner##"] = buscaCelda(ws, "INNER IP")
    dic["##gateway_security##"] = buscaCelda(ws, "Security Gateway IP")
    dic["##ip1_mme1##"] = buscaCelda(ws, "MME1 (IP1/IP2)").split("/")[0]
    dic["##ip1_mme2##"] = buscaCelda(ws, "MME2 (IP1/IP2)").split("/")[0]
    dic["##ip1_mme3##"] = buscaCelda(ws, "MME3 (IP1/IP2)").split("/")[0]
    dic["##ip1_mme4##"] = buscaCelda(ws, "MME4 (IP1/IP2)").split("/")[0]

    if "L1800" in xml:
        dic["##PrachCS L1800##"] = buscaCelda(ws, "PrachCS L1800")
        dic["##Physical Layer Cell Identity L1800##"] = buscaCelda(ws, "Physical Layer Cell Identity L1800")
        dic["##RACH root sequence L1800##"] = buscaCelda(ws, "RACH root sequence L1800")
    elif "L2600" in xml:
        dic["##PrachCS L2600##"] = buscaCelda(ws, "PrachCS L2600")
        dic["##Physical Layer Cell Identity L2600##"] = buscaCelda(ws, "Physical Layer Cell Identity L2600")
        dic["##RACH root sequence L2600##"] = buscaCelda(ws, "RACH root sequence L2600")

    # === ADVERTENCIA SI HAY VARIABLES VACÍAS ===
    for v in dic:
        if dic[v] == "":
            print(f"⚠️ WARNING: Variable {v} vacía")

    # === SUSTITUIR VARIABLES EN XML ===
    with open(xml, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()

    for v in dic:
        if isinstance(dic[v], list):
            for i in range(len(dic[v])):
                contenido = contenido.replace(f"{v}{i}##", f"{dic[v][i]}")
        else:
            contenido = contenido.replace(f"{v}", f"{dic[v]}")

    enb = f"ENB{dic['##mr_bts_name##']}".replace("_", "-")
    contenido = contenido.replace(f"ENB{dic['##mr_bts_name##']}", enb)

    # === GUARDAR ARCHIVO FINAL ===
    with open("salida.xml", "w", encoding="utf-8") as f:
        f.write(contenido)

    print("✅ Archivo salida.xml generado correctamente.")
    os.remove(xlsx)
    return "✅ Archivo salida.xml generado correctamente."


def buscaCelda(hoja, valor_buscado):
    """Busca un valor en la primera fila y devuelve el valor de la segunda."""
    for celda in hoja[1]:
        if celda.value == valor_buscado:
            celda_objetivo = f"{celda.column_letter}2"
            return hoja[celda_objetivo].value
    return ""
