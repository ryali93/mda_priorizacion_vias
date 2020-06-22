import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "50%"

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
    red_vial_feature = arcpy.Merge_management([via_nacional, via_departamental, via_vecinal], "in_memory\\via_merge")
    return red_vial_feature

def area_natural_protegida(feature, red_vial):
    mfl_ft = arcpy.MakeFeatureLayer_management(feature, "mfl_ft")
    mfl_rv = arcpy.MakeFeatureLayer_management(red_vial, "mfl_rv")
    arcpy.Intersect_analysis(in_features=[mfl_ft, mfl_rv],
                             out_feature_class="intersect_out_mfl")
    arcpy.Dissolve_management(tempLayer, outFeatureClass, dissolveFields, "", "SINGLE_PART", "DISSOLVE_LINES")

    arcpy.TableToTable_conversion(in_rows, out_path, out_name, {where_clause}, {field_mapping})

def process():
    red_vial_feature = red_vial()
    area_natural_protegida(anp_teu, red_vial_feature)

def main():
    pass
