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

def polos_intensificacion(feature, cobertura, red_vial_pol):
    feature_clip = cortar_region(feature, REGION[1])
    # feature_clip = arcpy.MakeFeatureLayer_management(os.path.join(SCRATCH, "clip_region"), "feature_clip")
    arcpy.AddMessage("feature_clip")
    sql = u"Cobertura = 'NO BOSQUE 2000' Or Cobertura = 'PÉRDIDA 2001-201'"
    mfl_bosque = arcpy.MakeFeatureLayer_management(feature_clip, "mfl_bosque", sql)
    dissol_bosque = arcpy.Dissolve_management(mfl_bosque, os.path.join(SCRATCH,"dissol_bosque"), [], [],
                                              "MULTI_PART", "DISSOLVE_LINES")
    arcpy.AddMessage("dissol_bosque")

    sql_2 = u"Cobertura = 'BOSQUE 2018'"
    mfl_bosque_2 = arcpy.MakeFeatureLayer_management(feature_clip, "mfl_bosque_2", sql_2)
    dissol_bosque_2 = arcpy.Dissolve_management(mfl_bosque_2, os.path.join(SCRATCH,"dissol_bosque_2"), [], [],
                                                "MULTI_PART", "DISSOLVE_LINES")
    arcpy.AddMessage("dissol_bosque_2")
    cobertura_erase = arcpy.Erase_analysis(cobertura, dissol_bosque_2, os.path.join(SCRATCH, "cobertura_erase"))
    arcpy.AddMessage("cobertura_erase")

    cobertura_union = arcpy.Union_analysis(in_features=[[dissol_bosque, ""], [cobertura_erase, ""]],
                                           out_feature_class=os.path.join(SCRATCH, "cobertura_union"),
                                           join_attributes="ALL")
    arcpy.AddMessage("cobertura_union")

    cobertura_dissol = arcpy.Dissolve_management(in_features=cobertura_union, out_feature_class=os.path.join(SCRATCH,"cobertura_dissol"),
                                                 multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    arcpy.AddMessage("cobertura_dissol")

    polos_mfl = arcpy.Intersect_analysis(in_features=[[cobertura_dissol, ""], [pot_product, ""], [red_vial_pol, ""]],
                                         out_feature_class=os.path.join(SCRATCH,"polos_intersect1"))
    # polos_mfl = os.path.join(SCRATCH, "polos_intersect1")
    arcpy.AddMessage("polos_intersect")
    sql_3 = "PP = 'AP-AC-FL' Or PP = 'AP-AC' Or PP = 'AP-AC'"
    field = "PNTPOLOS"
    # polos_mfl = arcpy.Select_analysis(polos_intersect, os.path.join(SCRATCH, "polos_mfl"), sql_3)
    arcpy.AddField_management(polos_mfl, field, "DOUBLE")
    arcpy.AddField_management(polos_mfl, "AREA_GEO", "DOUBLE")
    if mod_geom == 'cf':
        arcpy.CalculateField_management(polos_mfl, "AREA_GEO", "!shape.area@hectares!","PYTHON_9.3")
    with arcpy.da.UpdateCursor(polos_mfl, ["SHAPE@", "AREA_B5KM", field, "AREA_GEO"]) as cursor:
        for row in cursor:
            if mod_geom == 'cf':
                area_ha = row[3]
            else:
                area_ha = row[0].getArea("GEODESIC", "HECTARES")
                row[3] = area_ha
            row[2] = area_ha / row[1]
            cursor.updateRow(row)
    del cursor

    cobertura_dissol_f = arcpy.Dissolve_management(polos_mfl, os.path.join(SCRATCH, "cobertura_dissol_f"),
                                                   dissolve_field=["ID_RV"], statistics_fields=[[field, "SUM"]],
                                                   multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    arcpy.AddMessage("cobertura_dissol_f")
    table_cob_agricola = arcpy.TableToTable_conversion(cobertura_dissol_f, PATH_GDB,
                                                       out_name="RV_POLOS_{}".format(REGION[0]))
    return dissol_bosque, cobertura_erase, table_cob_agricola

def process():
    red_vial_pol = arcpy.GetParameterAsText(2)
    fc_distritos = copy_distritos(distritos)
    fc_cob_agricola_1 = cobertura_agricola_1(cob_agricola, fc_distritos)
    cob_agri_sinbosque, bosque_nobosque, tabla_polos = polos_intensificacion(bosque, fc_cob_agricola_1, red_vial_pol)
    arcpy.AddMessage("Termino proceso de Polos")
    arcpy.SetParameterAsText(3, tabla_polos)

def main():
    process()

if __name__ == '__main__':
    main()

