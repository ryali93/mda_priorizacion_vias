# -*- coding: utf-8 -*-
from settings import *
from funciones import *

mod_geom = "cf" # Calculatefield

def cobertura_agricola_1(feature, distrito):
    sql = "IDDPTO = '{}'".format(id_region)
    mfl_distrito = arcpy.MakeFeatureLayer_management(distrito, "mfl_distrito", sql)
    mfl_cob_agricola = arcpy.MakeFeatureLayer_management(feature, "mfl_cob_agricola")
    cob_agricola_intersect = arcpy.Intersect_analysis(in_features=[[mfl_distrito, ""], [mfl_cob_agricola, ""]],
                                                      out_feature_class= os.path.join(SCRATCH, "cob_agricola_intersect"),
                                                      join_attributes="ALL", cluster_tolerance="",
                                                      output_type="INPUT")
    cob_agricola_dissol = arcpy.Dissolve_management(in_features=cob_agricola_intersect,
                                                    out_feature_class= os.path.join( SCRATCH, "cob_agricola_dissol"),
                                                    dissolve_field=[], statistics_fields=[], multi_part="MULTI_PART",
                                                    unsplit_lines="DISSOLVE_LINES")
    return cob_agricola_dissol

def cobertura_agricola_2(feature, red_vial_pol):
    cob_agricola_intersect2 = arcpy.Intersect_analysis(in_features=[[feature, ""], [red_vial_pol, ""]],
                             out_feature_class=os.path.join(SCRATCH,"cob_agricola_intersect2"),
                             join_attributes="ALL",
                             cluster_tolerance="",
                             output_type="INPUT")
    field = "P_CAGRI"
    arcpy.AddField_management(cob_agricola_intersect2, field, "DOUBLE")
    arcpy.AddField_management(cob_agricola_intersect2, "AREA_GEO", "DOUBLE")
    if mod_geom == 'cf':
        arcpy.CalculateField_management(cob_agricola_intersect2, "AREA_GEO", "!shape.area@hectares!","PYTHON_9.3")
    with arcpy.da.UpdateCursor(cob_agricola_intersect2, ["SHAPE@", "AREA_B5KM", "P_CAGRI","AREA_GEO"]) as cursor:
        for row in cursor:
            if mod_geom == 'cf':
                area_ha = row[3]
            else:
                area_ha = row[0].getArea("GEODESIC", "HECTARES")
                row[3] = area_ha
            row[2] = area_ha / row[1]

            cursor.updateRow(row)
    del cursor
    cob_agricola_dissol = arcpy.Dissolve_management(cob_agricola_intersect2, os.path.join(SCRATCH,"cob_agricola_dissol"),
                                                    dissolve_field=["ID_RV"],
                                                    statistics_fields=[[field, "SUM"]], multi_part="MULTI_PART",
                                                    unsplit_lines="DISSOLVE_LINES")
    table_cob_agricola = arcpy.TableToTable_conversion(cob_agricola_dissol, PATH_GDB,
                                                       out_name="RV_CAGRI_{}".format(REGION[0]))
    return table_cob_agricola

def process():
    red_vial_pol = arcpy.GetParameterAsText(2)
    fc_distritos = copy_distritos(distritos)
    fc_cob_agricola_1 = cobertura_agricola_1(cob_agricola, fc_distritos)
    arcpy.AddMessage("Se realizo la primera parte del proceso de cobertura agricola")
    tabla_cob_agric = cobertura_agricola_2(fc_cob_agricola_1, red_vial_pol)
    arcpy.AddMessage("Termino proceso de Cobertura agricola")
    arcpy.SetParameterAsText(3, tabla_cob_agric)

def main():
    process()

if __name__ == '__main__':
    main()
