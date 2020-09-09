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
nom_reg = "CUSCO"
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

# Paths
# INSUMOS
departamentos = os.path.join(PATH_GDB, "insumos/departamentos_peru")
distritos = os.path.join(PATH_GDB, "insumos/distritos_peru")

# Red vial
via_nacional = os.path.join(PATH_GDB, r"Insumos/red_vial_nacional_2018MTC")
via_departamental = os.path.join(PATH_GDB, r"Insumos/red_vial_departamental_2018MTC")
via_vecinal = os.path.join(PATH_GDB, r"Insumos/red_vial_vecinal_2019MTC")
# via_local = os.path.join(PATH_GDB, r"Insumos/rv_{}_new".format(REGION[3]))

# Areas naturales protegidas
anp_acr = os.path.join(PATH_GDB, u"Ambiental/Área_de_Conservación_Regional")
anp_def = os.path.join(PATH_GDB, u"Ambiental/Área_de_Conservación_Privada")
anp_pri = os.path.join(PATH_GDB, u"Ambiental/Áreas_Naturales_Protegidas_Definitivas")
anp_amr = os.path.join(PATH_GDB, u"Ambiental/Zona_de_amortiguamiento")
anp_zr = os.path.join(PATH_GDB, u"Ambiental/Zonas_Reservadas")

# Recursos turisticos
fc_turis = os.path.join(PATH_GDB, u"Economico/atractivos_turisticos")

# Bosques Vulnerables
bosq_vuln = os.path.join(PATH_GDB, r"Ambiental\BV_{}_2018".format(REGION[3]))

# Restauracion ROAM
fc_roam = os.path.join(PATH_GDB, r"Ambiental\ROAM_{}".format(REGION[3]))

# Polos de intensificacion productiva en cobertura agricola
bosque = os.path.join(PATH_GDB, r"Ambiental\Bosque_No_Bosque_2018_peru")
pot_product = os.path.join(PATH_GDB, r"Economico\polos_{}_2018".format(REGION[3]))

# Brechas sociales
tbp_brechas = os.path.join(PATH_GDB,r'puntaje_brechas_sociales')

# Estadistica agraria
tbp_estagr = os.path.join(PATH_GDB,r'puntaje_estadistica_agraria_2018')

# Habitantes por centro poblado
ccpp = os.path.join(PATH_GDB, r"Social\ccpp_peru_2017")

# Cobertura agricola
cob_agricola = os.path.join(PATH_GDB, r"Economico\cobertura_agricola_peru_2018")


TOOL_NAME = {
    'T01': 'EstructuraDirectorio',

    'T02': 'pmmUnidadesGeologicas',
    'T03': 'pmmFallasGeologicas',
    'T04': 'pmmDepositosMinerales',
    'T05': 'pmmGeoquimica',
    'T06': 'pmmSensoresRemotos',
    'T07': 'PotencialMineroMetalico'
}