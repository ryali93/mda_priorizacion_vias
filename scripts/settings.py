# -*- coding: utf-8 -*-
import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "100%"
# arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(32718)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PATH_GDB = os.path.join(BASE_DIR, "PRVDA.gdb")
SCRATCH = arcpy.env.scratchGDB

# Paths
# INSUMOS
departamentos = os.path.join(PATH_GDB, "insumos/departamentos_peru")
distritos = os.path.join(PATH_GDB, "insumos/distritos_peru")

# Red vial
via_nacional = os.path.join(PATH_GDB, r"Insumos/red_vial_vecinal_2019MTC")
via_departamental = os.path.join(PATH_GDB, r"Insumos/red_vial_nacional_2018MTC")
via_vecinal = os.path.join(PATH_GDB, r"Insumos/red_vial_departamental_2018MTC")
via_local = os.path.join(PATH_GDB, r"Insumos/rv_sanmartin_new")

# Areas naturales protegidas
anp_acr = os.path.join(PATH_GDB, u"Ambiental/Área_de_Conservación_Regional")
anp_def = os.path.join(PATH_GDB, u"Ambiental/Área_de_Conservación_Privada")
anp_pri = os.path.join(PATH_GDB, u"Ambiental/Áreas_Naturales_Protegidas_Definitivas")
anp_amr = os.path.join(PATH_GDB, u"Ambiental/Zona_de_amortiguamiento")
anp_zr = os.path.join(PATH_GDB, u"Ambiental/Zonas_Reservadas")

# Recursos turisticos
fc_turis = os.path.join(PATH_GDB, u"Economico/atractivos_turisticos")

# Bosques Vulnerables
bosq_vuln = os.path.join(PATH_GDB, r"Ambiental\BV_sanmartin_2018")

# Restauracion ROAM
fc_roam = os.path.join(PATH_GDB, r"Ambiental\ROAM_sanmartin")

# Brechas sociales
tbp_brechas = os.path.join(PATH_GDB,r'puntaje_brechas_sociales')

# Estadistica agraria
tbp_estagr = os.path.join(PATH_GDB,r'puntaje_estadistica_agraria_2018')

# Habitantes por centro poblado
ccpp = os.path.join(PATH_GDB, r"Social\ccpp_peru_2017")

# Cobertura agricola
cob_agricola = os.path.join(PATH_GDB, r"Economico\cobertura_agricola_peru_2018")

# Polos de intensificacion productiva en cobertura agricola
bosque = os.path.join(PATH_GDB, r"Ambiental\Bosque_No_Bosque_2018_peru")
pot_product = os.path.join(PATH_GDB, r"Economico\polos_sanmartin_2018")

REGIONES = {1:  ["AMA", "AMAZONAS", 417365],
            2:  ["ANC", "ANCASH", 813381],
            3:  ["APU", "APURIMAC", 813381],
            4:  ["ARE", "AREQUIPA", 813381],
            5:  ["AYA", "AYACUCHO", 813381],
            6:  ["CAJ", "CAJAMARCA", 813381],
            7:  ["CAL", "CALLAO", 813381],
            8:  ["CUS", "CUSCO", 813381],
            9:  ["HUA", "HUANCAVELICA", 813381],
            10: ["HUA", "HUANUCO", 813381],
            11: ["ICA", "ICA", 813381],
            12: ["JUN", "JUNIN", 813381],
            13: ["LA", "LA LIBERTAD", 813381],
            14: ["LAM", "LAMBAYEQUE", 813381],
            15: ["LIM", "LIMA", 813381],
            16: ["LOR", "LORETO", 813381],
            17: ["MAD", "MADRE DE DIOS", 813381],
            18: ["MOQ", "MOQUEGUA", 813381],
            19: ["PAS", "PASCO", 813381],
            20: ["PIU", "PIURA", 813381],
            21: ["PUN", "PUNO", 813381],
            22: ["SM", "SAN MARTIN", 813381],
            23: ["TAC", "TACNA", 813381],
            24: ["TUM", "TUMBES", 813381],
            25: ["UCA", "UCAYALI", 813381]}

cod_reg = 22 # Elegir la region que corresponde

REGION = REGIONES[cod_reg]
POB_REGION  = REGION[2]
id_region = str(cod_reg).zfill(2)