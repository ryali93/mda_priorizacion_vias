# -*- coding: utf-8 -*-
from settings import *
import pandas as pd

REGION = REGIONES[22]
id_region = REGION[0]
sql = "{} = '{}'".format("DEPARTAMEN", REGION[1])

# Functions
def red_vial(feature):
    '''
    Devuelve las capas de lineas y poligonos a partir de la capa de vias con merge corregido
    '''
    mfl_rv = arcpy.MakeFeatureLayer_management(feature, 'mfl_rv')
    desc = arcpy.Describe(mfl_rv)
    id_dep = REGION[0]
    fieldname = "ID_RV"
    field_area = "AREA_B5KM"
    oidname = desc.OIDFieldName
    arcpy.AddField_management(mfl_rv, fieldname, "TEXT", "", "", 25)

    # Se crea el identificador unico para red vial
    with arcpy.da.UpdateCursor(mfl_rv, [oidname, fieldname]) as cursor:
        for row in cursor:
            row[1] = str(id_dep) + "_" + str(row[0])
            cursor.updateRow(row)
    del cursor
    buffer_name = 'B5KM_RV_{}'.format(id_dep)
    bf = arcpy.Buffer_analysis(in_features=mfl_rv, out_feature_class='in_memory\\{}'.format(buffer_name),
                               buffer_distance_or_field="5 Kilometers", line_side="FULL", line_end_type="ROUND",
                               dissolve_option="NONE", dissolve_field=[], method="PLANAR")
    bf_fc = bf.getOutput(0)

    arcpy.AddField_management(bf_fc, field_area, "DOUBLE")
    mfl_buffer = arcpy.MakeFeatureLayer_management(bf_fc, "mfl_buffer")

    # Se calcula el area del buffer 5km para read vial
    with arcpy.da.UpdateCursor(mfl_buffer, ["SHAPE@", field_area]) as cursor:
        for row in cursor:
            # area en hectareas
            area_ha = row[0].getArea("GEODESIC","HECTARES")
            row[1] = area_ha
            cursor.updateRow(row)
    return mfl_rv, mfl_buffer

def copy_distritos(distritos):
    fc_dist = arcpy.CopyFeatures_management(distritos, os.path.join(SCRATCH, "distritos"))
    return fc_dist

def area_natural_protegida(feature, red_vial_line):
    fieldname1 = "ANPC_NOMB"
    fieldname2 = "ANPC_NOMB"
    mfl_ft = arcpy.MakeFeatureLayer_management(feature, "mfl_ft")
    mfl_rv = arcpy.MakeFeatureLayer_management(red_vial_line, "mfl_rv")

    intersect_out_mfl = arcpy.Intersect_analysis([mfl_ft, mfl_rv], "in_memory\\intersect_anp")

    field_names = [f.name for f in arcpy.ListFields(intersect_out_mfl)]

    dissol_anp = arcpy.Dissolve_management(in_features=intersect_out_mfl,
                                           out_feature_class="in_memory\\dissol_anp", dissolve_field=["ID_RV"],
                                           statistics_fields=[[fieldname1, "MAX"], [fieldname2, "MAX"]],
                                           multi_part="MULTI_PART",
                                           unsplit_lines="DISSOLVE_LINES")
    # ["ANPC_NOMB", "MAX"], ["ANPC_CAT", "MAX"]

    table_anp = arcpy.TableToTable_conversion(dissol_anp, PATH_GDB, "RV_{}_ANP".format(REGION[0]))
    return table_anp

def recursos_turisticos(feature, red_vial_pol):
    sql = "DPTO = 'San Martin'"
    fieldname = "P_RECTURIS"
    mfl_turis = arcpy.MakeFeatureLayer_management(feature, "mfl_turis", sql)
    buffer_turis = arcpy.Buffer_analysis(in_features=mfl_turis, out_feature_class='in_memory\\buffer_turis',
                                         buffer_distance_or_field="10 Kilometers", line_side="FULL",
                                         line_end_type="ROUND", dissolve_option="NONE",
                                         dissolve_field=[], method="PLANAR")
    buffer_turis = buffer_turis.getOutput(0)

    dissol_turis = arcpy.Dissolve_management(in_features=buffer_turis,
                                             out_feature_class='in_memory\\dissol_turis',
                                             dissolve_field=[],
                                             statistics_fields=[], multi_part="MULTI_PART",
                                             unsplit_lines="DISSOLVE_LINES")
    intersect_turis = arcpy.Intersect_analysis(in_features=[[dissol_turis, ""], [red_vial_pol, ""]],
                                               out_feature_class='in_memory\\intersect_turis',
                                               join_attributes="ALL",
                                               cluster_tolerance="", output_type="INPUT")
    isc_fc = intersect_turis.getOutput(0)

    arcpy.AddField_management(isc_fc, fieldname, "DOUBLE")

    # Se calcula el porcentaje de area de buffer_turis sobre red_vial_pol
    with arcpy.da.UpdateCursor(buffer_turis, ["SHAPE@", fieldname, "AREA_B5KM"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC","HECTARES")
            row[1] = area_ha/row[2]
            cursor.updateRow(row)
    dissol_isc_rectur = arcpy.Dissolve_management(in_features=isc_fc,
                                                  out_feature_class='in_memory\\dissol_isc_rectur' ,
                                                  dissolve_field=["ID_RV"],
                                                  statistics_fields=[[fieldname, "SUM"]],
                                                  multi_part="MULTI_PART",
                                                  unsplit_lines="DISSOLVE_LINES")
    table_tur = arcpy.TableToTable_conversion(dissol_isc_rectur, PATH_GDB, "RV_{}_TUR".format(REGION[0]))
    return table_tur

def bosque_vulnerable(feature, red_vial_pol):
    sql = "Riesgo in ('Muy Alto','Alto','Mediano')"
    mfl_bv = arcpy.MakeFeatureLayer_management(feature,"mfl_bv",sql)

    intersect_bv = arcpy.Intersect_analysis(in_features=[[red_vial_pol, ""], [mfl_bv, ""]], 
                                                out_feature_class='in_memory\\intersect_bv', 
                                                join_attributes="ALL", 
                                                cluster_tolerance="", output_type="INPUT")
    dissol_isc_bv = arcpy.Dissolve_management(in_features=intersect_bv, 
                                                out_feature_class='in_memory\\dissol_isc_bv', 
                                                dissolve_field=["ID_RV", "AREA_B5KM"], 
                                                statistics_fields=[], 
                                                multi_part="MULTI_PART", 
                                                unsplit_lines="DISSOLVE_LINES")

    arcpy.AddField_management(dissol_isc_bv, "AREA_GEO", "DOUBLE")
    arcpy.AddField_management(dissol_isc_bv, "PNTBV", "DOUBLE")

    with arcpy.da.UpdateCursor(dissol_isc_bv, ["SHAPE@","AREA_GEO","PNTBV","AREA_B5KM"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC","HECTARES")
            row[1] = area_ha
            row[2] = area_ha/row[3]
            cursor.updateRow(row)

    table_bv = arcpy.TableToTable_conversion(dissol_isc_bv, PATH_GDB, "RV_{}_BV".format(REGION[0]))
    return table_bv

def restauracion(feature, red_vial_pol):
    mfl_roam = arcpy.MakeFeatureLayer_management(feature,"mfl_roam")

    intersect_roam = arcpy.Intersect_analysis(in_features=[[red_vial_pol, ""], [mfl_roam, ""]], 
                                                # out_feature_class='in_memory\\intersect_roam', 
                                                out_feature_class=os.path.join(SCRATCH, "intersect_roam"), 
                                                join_attributes="ALL", 
                                                cluster_tolerance="", output_type="INPUT")

    dissol_isc_roam = arcpy.Dissolve_management(in_features=intersect_roam, 
                                                out_feature_class='in_memory\\dissol_isc_roam', 
                                                dissolve_field=["ID_RV", "AREA_B5KM"], 
                                                statistics_fields=[], 
                                                multi_part="MULTI_PART", 
                                                unsplit_lines="DISSOLVE_LINES")

    arcpy.AddField_management(dissol_isc_roam, "AREA_GEO", "DOUBLE")
    arcpy.AddField_management(dissol_isc_roam, "PNTROAM", "DOUBLE")

    with arcpy.da.UpdateCursor(dissol_isc_roam, ["SHAPE@","AREA_GEO","PNTROAM","AREA_B5KM"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC","HECTARES")
            row[1] = area_ha
            row[2] = area_ha/row[3]
            cursor.updateRow(row)

    table_roam = arcpy.TableToTable_conversion(dissol_isc_roam, PATH_GDB, "RV_{}_ROAM".format(REGION[0]))
    return table_roam

def brechas_sociales(distritos, red_vial_pol, tbpuntaje):

    mfl_dist = arcpy.MakeFeatureLayer_management(distritos,"mfl_dist")

    ubigeo = "IDDIST"
    brecha = "PUNT_BRECHAS"

    arcpy.AddField_management(mfl_dist, brecha , "DOUBLE")

    df_brecha = {str(int(x[0])).zfill(6):x[1] for x in arcpy.da.SearchCursor(tbpuntaje,["UBIGEO",brecha])}

    # Actualizamos el campo brecha con los valores de la tabla de puntaje
    with arcpy.da.UpdateCursor(mfl_dist, [ubigeo,brecha]) as cursor:
        for row in cursor:

            if df_brecha.get(row[0]):

                respuesta = df_brecha.get(row[0])
                row[1] = respuesta
                cursor.updateRow(row)

    intersect_bs = arcpy.Intersect_analysis(in_features=[[red_vial_pol, ""], [mfl_dist, ""]],
                                            out_feature_class='in_memory\\intersect_bs', 
                                            join_attributes="ALL", cluster_tolerance="", 
                                            output_type="INPUT")

    dissol_bs = arcpy.Dissolve_management(in_features=intersect_bs, 
                                            out_feature_class='in_memory\\dissol_bs', 
                                            dissolve_field=["ID_RV", "AREA_B5KM", "PUNT_BRECHAS"], 
                                            statistics_fields=[], multi_part="MULTI_PART", 
                                            unsplit_lines="DISSOLVE_LINES")

    arcpy.AddField_management(dissol_bs, "AREA_GEO", "DOUBLE")
    arcpy.AddField_management(dissol_bs, "PNTBRECHAS", "DOUBLE")

    with arcpy.da.UpdateCursor(dissol_bs, ["SHAPE@","AREA_GEO","PNTBRECHAS","AREA_B5KM"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC","HECTARES")
            row[1] = area_ha
            row[2] = area_ha/row[3]
            cursor.updateRow(row)

    table_bs = arcpy.TableToTable_conversion(dissol_bs, PATH_GDB, "RV_{}_BS".format(REGION[0]))
    return table_bs

def estadistica_agraria(distritos, red_vial_pol, tbpuntaje):

    mfl_dist = arcpy.MakeFeatureLayer_management(distritos,"mfl_dist")

    ubigeo = "IDDIST"
    estad_agr = "P_ESTAD"

    arcpy.AddField_management(mfl_dist, estad_agr , "TEXT","", "", 125)

    filtro = "UBIGEO is not NULL"

    df_estad_agr = {str(int(x[0])).zfill(6):x[1] for x in arcpy.da.SearchCursor(tbpuntaje,["UBIGEO",estad_agr], filtro)}

    # Actualizamos el campo P_ESTAD con los valores de la tabla de puntaje
    with arcpy.da.UpdateCursor(mfl_dist, [ubigeo,estad_agr]) as cursor:
        for row in cursor:

            if df_estad_agr.get(row[0]):                
            
                respuesta = df_estad_agr.get(row[0])
                row[1] = respuesta
                cursor.updateRow(row)


    intersect_ea = arcpy.Intersect_analysis(in_features=[[red_vial_pol, ""], [mfl_dist, ""]], 
                                            out_feature_class='in_memory\\intersect_ea', 
                                            join_attributes="ALL", 
                                            cluster_tolerance="", output_type="INPUT")
    dissol_ea = arcpy.Dissolve_management(in_features=intersect_ea, 
                                            out_feature_class='in_memory\\dissol_ea', 
                                            dissolve_field=["ID_RV", "AREA_B5KM", "P_ESTAD"], 
                                            statistics_fields=[], multi_part="MULTI_PART", 
                                            unsplit_lines="DISSOLVE_LINES")

    arcpy.AddField_management(dissol_ea, "AREA_GEO", "DOUBLE")
    arcpy.AddField_management(dissol_ea, "PNTESTAGRI", "DOUBLE")

    with arcpy.da.UpdateCursor(dissol_ea, ["SHAPE@","AREA_GEO","PNTESTAGRI","AREA_B5KM"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC","HECTARES")
            row[1] = area_ha
            row[2] = area_ha/row[3]
            cursor.updateRow(row)

    table_ea = arcpy.TableToTable_conversion(dissol_ea, PATH_GDB, "RV_{}_EA".format(REGION[0]))
    return table_ea

def habitante_ccpp(feature, red_vial_pol):
    mfl_ccpp = arcpy.MakeFeatureLayer_management(feature, "ccpp")
    arcpy.AddField_management(mfl_ccpp, "REPREPOBLA", "DOUBLE")

    with arcpy.da.UpdateCursor(mfl_ccpp, ["POB__2017_","REPREPOBLA"]) as cursor:
        for x in cursor:
            x[1] = x[0] / pob_sm
            cursor.updateRow(x)
    intersect_ccpp = arcpy.Intersect_analysis(in_features=[[mfl_ccpp, ""], [red_vial_pol, ""]],
                                                 out_feature_class="in_memory\\intersect_ccpp",
                                                 join_attributes="ALL")
    dissol_ccpp = arcpy.Dissolve_management(in_features=intersect_ccpp,
                                            out_feature_class="in_memory\\dissol_ccpp",
                                            dissolve_field=["ID_RV"], statistics_fields=[["REPREPOBLA", "SUM"]],
                                            multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    table_ccpp = arcpy.TableToTable_conversion(dissol_ccpp, PATH_GDB, "RV_{}_CCPP".format(REGION[0]))
    return table_ccpp

def cobertura_agricola_1(feature, distrito):
    sql = "IDDPTO = '{}'".format(id_region)
    mfl_distrito = arcpy.MakeFeatureLayer_management(distrito, "mfl_distrito")
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
    with arcpy.da.UpdateCursor(cob_agricola_intersect2, ["SHAPE@", "AREA_B5KM", "P_CAGRI"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC", "HECTARES")
            row[2] = area_ha / row[1]
            cursor.updateRow(row)
    cob_agricola_dissol = arcpy.Dissolve_management(cob_agricola_intersect2, os.path.join(SCRATCH,"cob_agricola_dissol"),
                                                    dissolve_field=["ID_RV"],
                                                    statistics_fields=[[field, "SUM"]], multi_part="MULTI_PART",
                                                    unsplit_lines="DISSOLVE_LINES")
    table_cob_agricola = arcpy.TableToTable_conversion(cob_agricola_dissol, PATH_GDB,
                                                       out_name="tb_cagri_{}".format(REGION[0]))
    return table_cob_agricola

def polos_intensificacion(feature, cobertura, red_vial_pol):
    sql = u"Cobertura = 'NO BOSQUE 2000' Or Cobertura = 'PÉRDIDA 2001-201'"
    mfl_bosque = arcpy.MakeFeatureLayer_management(feature, "mfl_bosque", sql)
    dissol_bosque = arcpy.Dissolve_management(mfl_bosque, "in_memory\\dissol_bosque", [], [],
                                              "MULTI_PART", "DISSOLVE_LINES")

    sql_2 = u"Cobertura = 'BOSQUE 2018'"
    mfl_bosque_2 = arcpy.MakeFeatureLayer_management(dissol_bosque, "mfl_bosque_2", sql_2)
    dissol_bosque_2 = arcpy.Dissolve_management(mfl_bosque_2, "in_memory\\dissol_bosque_2", [], [],
                                                "MULTI_PART", "DISSOLVE_LINES")
    cobertura_erase = arcpy.Erase_analysis(cobertura, dissol_bosque_2, "in_memory\\cobertura_erase")

    cobertura_union = arcpy.Union_analysis(in_features=[[dissol_bosque, ""], [cobertura_erase, ""]],
                                           out_feature_class="in_memory\\cobertura_union",
                                           join_attributes="ALL", cluster_tolerance="", gaps="GAPS")

    cobertura_dissol = arcpy.Dissolve_management(in_features=cobertura_union, out_feature_class="cobertura_dissol",
                                                 multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

    polos_intersect = arcpy.Intersect_analysis(in_features=[[cobertura_dissol, ""], [pot_product, ""], [red_vial_pol, ""]],
                                               out_feature_class="in_memory\\polos_intersect")
    sql_3 = "PP = 'AP-AC-FL' Or PP = 'AP-AC' Or PP = 'AP-AC'"
    polos_mfl = arcpy.MakeFeatureLayer_management(polos_intersect, "polos_mfl", sql_3)
    arcpy.AddField_management(polos_mfl, "PNTPOLOS", "DOUBLE")

    field = "PNTPOLOS"
    with arcpy.UpdateCursor(polos_mfl, ["SHAPE@", "AREA_B5KM", field]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC", "HECTARES")
            row[2] = area_ha / row[1]
            cursor.updateRow(row)

    cobertura_dissol_f = arcpy.Dissolve_management(polos_mfl, "in_memory\\cobertura_dissol_f",
                                                   dissolve_field=["ID_RV"], statistics_fields=[[field, "SUM"]],
                                                   multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    table_cob_agricola = arcpy.TableToTable_conversion(cobertura_dissol_f, PATH_GDB,
                                                       out_name="tb_polos_{}".format(REGION[0]))
    return dissol_bosque, cobertura_erase, table_cob_agricola

def zona_degradada_sin_cob_agricola(cob_agri_sinbosque, bosque_nobosque, red_vial_pol):
    erase_zd = arcpy.Erase_analysis(bosque_nobosque, cob_agri_sinbosque, "in_memory\\bnb_sin_cob_agri")
    intersect_zd = arcpy.Intersect_analysis([[erase_zd, ""], [red_vial_pol, ""]], "in_memory\\zd_intersect")
    dissol_zd = arcpy.Dissolve_management(intersect_zd, "in_memory\\zd_dissol",["ID_RV", "AREA_B5KM"],
                                          statistics_fields=[], multi_part="MULTI_PART",
                                          unsplit_lines="DISSOLVE_LINES")

    arcpy.AddField_management(dissol_zd, "AREA_GEO", "DOUBLE")
    arcpy.AddField_management(dissol_zd, "PNTBRECHAS", "DOUBLE")

    with arcpy.da.UpdateCursor(dissol_zd, ["SHAPE@", "AREA_GEO", "PNTBRECHAS", "AREA_B5KM"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC", "HECTARES")
            row[1] = area_ha
            row[2] = area_ha / row[3]

    table_zd = arcpy.TableToTable_conversion(dissol_zd, PATH_GDB, "tb_{}_zd".format(REGION[0]))
    return table_zd

def process():
    fc_distritos = copy_distritos(distritos)
    red_vial_line, red_vial_pol = red_vial(via_merge)
    fc_cob_agricola_1 = cobertura_agricola_1(cob_agricola, fc_distritos)
    print("termino cob1")

    # tabla_anp = area_natural_protegida(anp_teu, red_vial_line)
    # tabla_turis = recursos_turisticos(fc_turis, red_vial_pol)
    # print(tabla_turis)
    # tabla_bv = bosque_vulnerable(bosq_vuln, red_vial_pol)
    
    # tabla_roam = restauracion(fc_roam, red_vial_pol)
    # tabla_bs = brechas_sociales(fc_distritos, red_vial_pol, tbp_brechas)
    # tabla_ea = estadistica_agraria(fc_distritos,red_vial_pol, tbp_estagr)
    tabla_cob_agric = cobertura_agricola_2(fc_cob_agricola_1, red_vial_pol)
    print(tabla_cob_agric)
    # cob_agri_sinbosque, bosque_nobosque, tabla_polos = polos_intensificacion(bosque, fc_cob_agricola_1, red_vial_pol)
    # tabla_zd = zona_degradada_sin_cob_agricola(cob_agri_sinbosque, bosque_nobosque, red_vial_pol)
    # tabla_ccpp = habitante_ccpp(ccpp, red_vial_pol)


def main():
    from datetime import datetime
    start_time = datetime.now()
    process()
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

if __name__ == '__main__':
    main()