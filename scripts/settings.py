# -*- coding: utf-8 -*-
import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "100%"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PATH_GDB = os.path.join(BASE_DIR, "PRVDA.gdb")
SCRATCH = arcpy.env.scratchGDB

# Elegir la region que corresponde IMPORTANTE
cod_reg = 22

REGIONES = {1:  ["AMA", "AMAZONAS", 417365, "amazonas"],
            2:  ["ANC", "ANCASH", 1139115, "ancash"],
            3:  ["APU", "APURIMAC", 424259, "apurimac"],
            4:  ["ARE", "AREQUIPA", 1460433, "arequipa"],
            5:  ["AYA", "AYACUCHO", 650940, "ayacucho"],
            6:  ["CAJ", "CAJAMARCA", 1427527, "cajamarca"],
            7:  ["CAL", "CALLAO", 1046953, "callao"],
            8:  ["CUS", "CUSCO", 1315220, "cusco"],
            9:  ["HUA", "HUANCAVELICA", 367252, "huancavelica"],
            10: ["HUA", "HUANUCO", 759962, "huanuco"],
            11: ["ICA", "ICA", 893292, "ica"],
            12: ["JUN", "JUNIN", 1316894, "junin"],
            13: ["LA", "LA LIBERTAD", 1888972, "lalibertad"],
            14: ["LAM", "LAMBAYEQUE", 1244821, "lambayeque"],
            15: ["LIM", "LIMA", 10135009, "lima"],
            16: ["LOR", "LORETO", 981897, "loreto"],
            17: ["MAD", "MADRE DE DIOS", 161204, "madrededios"],
            18: ["MOQ", "MOQUEGUA", 182017, "moquegua"],
            19: ["PAS", "PASCO", 272136, "pasco"],
            20: ["PIU", "PIURA", 1929970, "piura"],
            21: ["PUN", "PUNO", 1226936, "puno"],
            22: ["SM", "SAN MARTIN", 862459, "sanmartin"],
            23: ["TAC", "TACNA", 349056, "tacna"],
            24: ["TUM", "TUMBES", 234698, "tumbes"],
            25: ["UCA", "UCAYALI", 548998, "ucayali"]}

REGION = REGIONES[cod_reg]
POB_REGION  = REGION[2]
id_region = str(cod_reg).zfill(2)

# Paths
# INSUMOS
departamentos = os.path.join(PATH_GDB, "insumos/departamentos_peru")
distritos = os.path.join(PATH_GDB, "insumos/distritos_peru")

# Red vial
via_nacional = os.path.join(PATH_GDB, r"Insumos/red_vial_vecinal_2019MTC")
via_departamental = os.path.join(PATH_GDB, r"Insumos/red_vial_nacional_2018MTC")
via_vecinal = os.path.join(PATH_GDB, r"Insumos/red_vial_departamental_2018MTC")
via_local = os.path.join(PATH_GDB, r"Insumos/rv_{}_new".format(REGION[3]))

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
