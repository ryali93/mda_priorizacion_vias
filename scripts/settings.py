
import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "50%"

BASE_DIR = r''
PATH_GDB = os.path.join(BASE_DIR, "")
REGIONES = {"15": ["SM", "SAN MARTIN"]}
REGION = REGIONES["15"]
SCRATCH = arcpy.env.scratchGDB

# Paths

# Distritos
distritos = os.path.join(PATH_GDB, "Distritos")

# Red vial
via_nacional = os.path.join(PATH_GDB, "via_nacional")
via_departamental = os.path.join(PATH_GDB, "via_departamental")
via_vecinal = os.path.join(PATH_GDB, "via_vecinal")

via_merge = os.path.join(PATH_GDB, "via_merge")

# Areas naturales protegidas
anp_teu = os.path.join(PATH_GDB, "ANP_TEU")

# Recursos turisticos
fc_turis = os.path.join(PATH_GDB, "tur_features")

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