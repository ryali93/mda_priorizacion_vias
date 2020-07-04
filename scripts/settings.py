# -*- coding: utf-8 -*-
import arcpy
import os
import string

arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "100%"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# PATH_GDB = os.path.join(BASE_DIR, "PRVDA.gdb")
SCRATCH = arcpy.env.scratchGDB

# Elegir la region que corresponde IMPORTANTE

nom_reg = arcpy.GetParameterAsText(0)
PATH_GDB = arcpy.GetParameterAsText(1)

REGIONES = {"AMAZONAS":  ["AMA", "AMAZONAS", 417365, "amazonas", 1],
            "ANCASH":  ["ANC", "ANCASH", 1139115, "ancash", 2],
            "APURIMAC":  ["APU", "APURIMAC", 424259, "apurimac", 3],
            "AREQUIPA":  ["ARE", "AREQUIPA", 1460433, "arequipa", 4],
            "AYACUCHO":  ["AYA", "AYACUCHO", 650940, "ayacucho", 5],
            "CAJAMARCA":  ["CAJ", "CAJAMARCA", 1427527, "cajamarca", 6],
            "CALLAO":  ["CAL", "CALLAO", 1046953, "callao", 7],
            "CUSCO":  ["CUS", "CUSCO", 1315220, "cusco", 8],
            "HUANCAVELICA":  ["HUA", "HUANCAVELICA", 367252, "huancavelica", 9],
            "HUANUCO": ["HUA", "HUANUCO", 759962, "huanuco", 10],
            "ICA": ["ICA", "ICA", 893292, "ica", 11],
            "JUNIN": ["JUN", "JUNIN", 1316894, "junin", 12],
            "LA_LIBERTAD": ["LA", "LA LIBERTAD", 1888972, "lalibertad", 13],
            "LAMBAYEQUE": ["LAM", "LAMBAYEQUE", 1244821, "lambayeque", 14],
            "LIMA": ["LIM", "LIMA", 10135009, "lima", 15],
            "LORETO": ["LOR", "LORETO", 981897, "loreto", 16],
            "MADRE DE DIOS" : ["MAD", "MADRE DE DIOS", 161204, "madrededios", 17],
            "MOQUEGUA": ["MOQ", "MOQUEGUA", 182017, "moquegua", 18],
            "PASCO": ["PAS", "PASCO", 272136, "pasco", 19],
            "PIURA": ["PIU", "PIURA", 1929970, "piura", 20],
            "PUNO": ["PUN", "PUNO", 1226936, "puno", 21],
            "SAN_MARTIN": ["SM", "SAN MARTIN", 862459, "sanmartin", 22],
            "TACNA": ["TAC", "TACNA", 349056, "tacna", 23],
            "TUMBES": ["TUM", "TUMBES", 234698, "tumbes", 24],
            "UCAYALI": ["UCA", "UCAYALI", 548998, "ucayali", 25]}

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