import arcpy
import os

BASE_DIR = r''
PATH_GDB = r''
REGION = "SAN MARTIN"

# Paths
# Red vial
via_nacional = os.path.join(PATH_GDB, "via_nacional")
via_departamental = os.path.join(PATH_GDB, "via_departamental")
via_vecinal = os.path.join(PATH_GDB, "via_vecinal")

# Areas naturales protegidas
anp_teu = os.path.join(PATH_GDB, "ANP_TEU")

# Recursos turisticos
tur_features = os.path.join(PATH_GDB, "tur_features")

# Functions
def red_vial():
    sql = "{} = '{}'".format("DEPARTAMEN", REGION)
    arcpy.SelectLayerByAttribute_management(via_nacional, "NEW_SELECTION", sql)
    arcpy.SelectLayerByAttribute_management(via_departamental, "NEW_SELECTION", sql)
    arcpy.SelectLayerByAttribute_management(via_vecinal, "NEW_SELECTION", sql)
    return red_vial_feature

def area_natural_protegida(feature, red_vial):
    mfl_ft = arcpy.MakeFeatureLayer_management(feature, "mfl_ft")
    mfl_rv = arcpy.MakeFeatureLayer_management(red_vial, "mfl_rv")
    intersect_mfl = [mfl_ft, mfl_rv]
    intersect_out_mfl = "intersect_out_mfl"
    cluster_tolerance = 1.5
    arcpy.Intersect_analysis(intersect_mfl, intersect_out_mfl, "", cluster_tolerance, "point")
    arcpy.Dissolve_management(tempLayer, outFeatureClass, dissolveFields, "", "SINGLE_PART", "DISSOLVE_LINES")

def process():
    area_natural_protegida(anp_teu)

def main():
    pass
