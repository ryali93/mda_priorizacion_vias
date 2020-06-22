import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "50%"

BASE_DIR = r''
PATH_GDB = r''

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

REGION = REGIONES[22]
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
    arcpy.SelectLayerByAttribute_management(
        via_departamental, "NEW_SELECTION", sql)
    arcpy.SelectLayerByAttribute_management(via_vecinal, "NEW_SELECTION", sql)
    red_vial_feature = arcpy.Merge_management(
        [via_nacional, via_departamental, via_vecinal], "in_memory\\via_merge")
    return red_vial_feature


def get_blayers(rv_feature):
    rv_dep = arcpy.MakeFeatureLayer_management(rv_feature, 'rv_dep')
    desc = arcpy.Describe(rv_dep)
    id_dep = REGION[0]
    fieldname = "ID_RV"
    oidname = desc.OIDFieldName
    arcpy.AddField_management(rv_dep, fieldname, "TEXT", "", "", 25)

    # Se crea el identificador único para red vial
    with arcpy.da.UpdateCursor(rv_dep, [oidname, fieldname]) as cursor:
        for row in cursor:
            row[1] = id_dep + "_" + row[0]
            cursor.updateRow(row)

    bfname = 'B5KM_RV_{}'.format(id_dep)

    bf = arcpy.Buffer_analysis(in_features=rv_dep, out_feature_class='in_memory\\{}'.format(bfname), 
        buffer_distance_or_field="5 Kilometers", line_side="FULL", line_end_type="ROUND", dissolve_option="NONE", dissolve_field=[], method="PLANAR")
    bf_fc = bf.getOutput(0)

    bflayer = arcpy.MakeFeatureLayer_management(bf_fc, bfname)

    return rv_dep, bflayer


def area_natural_protegida(feature, red_vial):
    mfl_ft = arcpy.MakeFeatureLayer_management(feature, "mfl_ft")
    mfl_rv = arcpy.MakeFeatureLayer_management(red_vial, "mfl_rv")
    arcpy.Intersect_analysis(in_features=[mfl_ft, mfl_rv],
                             out_feature_class="intersect_out_mfl")
    arcpy.Dissolve_management(tempLayer, outFeatureClass,
                              dissolveFields, "", "SINGLE_PART", "DISSOLVE_LINES")

    arcpy.TableToTable_conversion(in_rows, out_path, out_name, {
                                  where_clause}, {field_mapping})


def process():
    red_vial_feature = red_vial()
    area_natural_protegida(anp_teu, red_vial_feature)


def main():
    pass
