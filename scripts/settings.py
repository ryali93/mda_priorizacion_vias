# -*- coding: utf-8 -*-
import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "100%"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 18S")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PATH_GDB = os.path.join(BASE_DIR, "PRVDA.gdb")
REGIONES = {"15": ["SM", "SAN MARTIN"]}
REGION = REGIONES["15"]
SCRATCH = arcpy.env.scratchGDB

# Paths

# INSUMOS
distritos = os.path.join(PATH_GDB, "insumos/distritos_peru")

# Red vial
via_nacional = os.path.join(PATH_GDB, "via_nacional")
via_departamental = os.path.join(PATH_GDB, "via_departamental")
via_vecinal = os.path.join(PATH_GDB, "via_vecinal")

via_merge = os.path.join(PATH_GDB, r"Insumos\rv_sanmartin_new")

# Areas naturales protegidas
anp_teu = os.path.join(PATH_GDB, u"Ambiental\Áreas_Naturales_Protegidas_Definitivas")

# Recursos turisticos
fc_turis = os.path.join(PATH_GDB, u"Economico/atractivos_turisticos")

# Bosques Vulnerables
bosq_vuln = os.path.join(PATH_GDB, "bosq_vulnerable")
# Restauracion ROAM
fc_roam = os.path.join(PATH_GDB, "roam_features")

# Brechas sociales
XLS_BRSOC = "ruta excel brechas sociales"

# Estadistica agraria
XLS_ESTAGR = "ruta excel Estadistica agraria"

# Habitantes por centro poblado
ccpp = os.path.join(PATH_GDB, "ccpp")

# Cobertura agricola
cob_agricola = os.path.join(PATH_GDB, "ngeo_Cob_Agricola_2018")

# Polos de intensificacion productiva en cobertura agricola
bosque = os.path.join(PATH_GDB, "bosque")
pot_product = os.path.join(PATH_GDB, "potencial_productivo")


REGIONES = {1:  ["AMA", "AMAZONAS"],
            2:  ["ANC", "ANCASH"],
            3:  ["APU", "APURIMAC"],
            4:  ["ARE", "AREQUIPA"],
            5:  ["AYA", "AYACUCHO"],
            6:  ["CAJ", "CAJAMARCA"],
            7:  ["CAL", "CALLAO"],
            8:  ["CUS", "CUSCO"],
            9:  ["HUA", "HUANCAVELICA"],
            10: ["HUA", "HUANUCO"],
            11: ["ICA", "ICA"],
            12: ["JUN", "JUNIN"],
            13: ["LA", "LA LIBERTAD"],
            14: ["LAM", "LAMBAYEQUE"],
            15: ["LIM", "LIMA"],
            16: ["LOR", "LORETO"],
            17: ["MAD", "MADRE DE DIOS"],
            18: ["MOQ", "MOQUEGUA"],
            19: ["PAS", "PASCO"],
            20: ["PIU", "PIURA"],
            21: ["PUN", "PUNO"],
            22: ["SAN", "SAN MARTIN"],
            23: ["TAC", "TACNA"],
            24: ["TUM", "TUMBES"],
            25: ["UCA", "UCAYALI"]}