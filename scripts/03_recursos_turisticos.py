# -*- coding: utf-8 -*-
from settings import *
from funciones import *

mod_geom = "cf" # Calculatefield

def recursos_turisticos(feature, red_vial_pol):
    sql = "DPTO = '{}'".format(string.capwords(REGION[1]))
    fieldname = "P_RECTURIS"
    mfl_turis = arcpy.MakeFeatureLayer_management(feature, "mfl_turis", sql)
    buffer_turis = arcpy.Buffer_analysis(in_features=mfl_turis, out_feature_class=os.path.join(SCRATCH, "buffer_turis_{}".format(REGION[0])),
                                         buffer_distance_or_field="10 Kilometers", line_side="FULL",
                                         line_end_type="ROUND", dissolve_option="NONE",
                                         dissolve_field=[], method="PLANAR")
    buffer_turis = buffer_turis.getOutput(0)

    arcpy.AddMessage("buffer_turis")
    dissol_turis = arcpy.Dissolve_management(in_features=buffer_turis,
                                             out_feature_class=os.path.join(SCRATCH, "dissol_turis_{}".format(REGION[0])),
                                             dissolve_field=[],
                                             statistics_fields=[], multi_part="MULTI_PART",
                                             unsplit_lines="DISSOLVE_LINES")
    arcpy.AddMessage("dissol_turis")
    intersect_turis = arcpy.Intersect_analysis(in_features=[[dissol_turis, ""], [red_vial_pol, ""]],
                                               out_feature_class=os.path.join(SCRATCH, "intersect_turis_{}1".format(REGION[0])),
                                               join_attributes="ALL",
                                               cluster_tolerance="", output_type="INPUT")
    isc_fc = intersect_turis.getOutput(0)
    arcpy.AddMessage("intersect_turis")
    arcpy.AddField_management(isc_fc, "AREA_GEO", "DOUBLE")
    arcpy.AddField_management(isc_fc, fieldname, "DOUBLE")

    # Se calcula el porcentaje de area de buffer_turis sobre red_vial_pol
    if mod_geom == 'cf':
        arcpy.CalculateField_management(isc_fc, "AREA_GEO", "!shape.area@hectares!", "PYTHON_9.3")
    with arcpy.da.UpdateCursor(isc_fc, ["SHAPE@", "AREA_GEO", fieldname, "AREA_B5KM"]) as cursor:
        for row in cursor:
            if mod_geom == 'cf':
                area_ha = row[1]
            else :
                area_ha = row[0].getArea("GEODESIC","HECTARES")
                row[1] = area_ha
            row[2] = area_ha/row[3]
            cursor.updateRow(row)
    del cursor
    arcpy.AddMessage("turis termino update")
    arcpy.AddMessage(isc_fc)
    arcpy.AddMessage(os.path.join(SCRATCH, "dissol_isc_rectur_{}2".format(REGION[0])))
    dissol_isc_rectur = arcpy.Dissolve_management(in_features=isc_fc,
                                                  out_feature_class=os.path.join(SCRATCH, "dissol_isc_rectur_{}2".format(REGION[0])) ,
                                                  dissolve_field=["ID_RV"],
                                                  statistics_fields=[[fieldname, "SUM"]],
                                                  multi_part="MULTI_PART",
                                                  unsplit_lines="DISSOLVE_LINES")

    arcpy.AddMessage("dissol_isc_rectur")
    table_tur = arcpy.TableToTable_conversion(dissol_isc_rectur, PATH_GDB, "RV_{}_TUR".format(REGION[0]))
    return table_tur

def process():
    red_vial_pol = arcpy.GetParameterAsText(2)
    tabla_turis = recursos_turisticos(fc_turis, red_vial_pol)
    arcpy.AddMessage("Termino proceso de Recursos turisticos")
    arcpy.SetParameterAsText(3, tabla_turis)

def main():
    process()

if __name__ == '__main__':
    main()
