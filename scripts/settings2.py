# -*- coding: utf-8 -*-
import arcpy
import os
import string
import uuid

arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "100%"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SCRATCH = arcpy.env.scratchGDB

# Elegir la region que corresponde IMPORTANTE
nom_reg = "UCAYALI"
PATH_GDB = r"E:\2020\mda\RED_VIAL_PERU.gdb"
# nom_reg = arcpy.GetParameterAsText(0)
# PATH_GDB = arcpy.GetParameterAsText(1)

REGIONES = {"AMAZONAS":  ["01", "AMA", "AMAZONAS", 417365, "amazonas"],
            "ANCASH":  ["02", "ANC", "ANCASH", 1139115, "ancash"],
            "APURIMAC":  ["03", "APU", "APURIMAC", 424259, "apurimac"],
            "AREQUIPA":  ["04", "ARE", "AREQUIPA", 1460433, "arequipa"],
            "AYACUCHO":  ["05", "AYA", "AYACUCHO", 650940, "ayacucho"],
            "CAJAMARCA":  ["06", "CAJ", "CAJAMARCA", 1427527, "cajamarca"],
            "CALLAO":  ["07", "CAL", "CALLAO", 1046953, "callao"],
            "CUSCO":  ["08", "CUS", "CUSCO", 1315220, "cusco"],
            "HUANCAVELICA":  ["09", "HUA", "HUANCAVELICA", 367252, "huancavelica"],
            "HUANUCO": ["10", "HUA", "HUANUCO", 759962, "huanuco"],
            "ICA": ["11", "ICA", "ICA", 893292, "ica"],
            "JUNIN": ["12", "JUN", "JUNIN", 1316894, "junin"],
            "LA_LIBERTAD": ["13", "LA", "LA LIBERTAD", 1888972, "lalibertad"],
            "LAMBAYEQUE": ["14", "LAM", "LAMBAYEQUE", 1244821, "lambayeque"],
            "LIMA": ["15", "LIM", "LIMA", 10135009, "lima"],
            "LORETO": ["16", "LOR", "LORETO", 981897, "loreto"],
            "MADRE_DE_DIOS" : ["17", "MAD", "MADRE DE DIOS", 161204, "madrededios"],
            "MOQUEGUA": ["18", "MOQ", "MOQUEGUA", 182017, "moquegua"],
            "PASCO": ["19", "PAS", "PASCO", 272136, "pasco"],
            "PIURA": ["20", "PIU", "PIURA", 1929970, "piura"],
            "PUNO": ["21", "PUN", "PUNO", 1226936, "puno"],
            "SAN_MARTIN": ["22", "SM", "SAN MARTIN", 862459, "sanmartin"],
            "TACNA": ["23", "TAC", "TACNA", 349056, "tacna"],
            "TUMBES": ["24", "TUM", "TUMBES", 234698, "tumbes"],
            "UCAYALI": ["25", "UCA", "UCAYALI", 548998, "ucayali"]}

REGION = REGIONES[nom_reg]
cod_reg = REGION[4]
POB_REGION  = REGION[2]
id_region = str(cod_reg).zfill(2)

# python_version = "PYTHON3"
python_version = "PYTHON_9.3"