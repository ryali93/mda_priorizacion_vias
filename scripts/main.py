# -*- coding: utf-8 -*-
from settings import *
from datetime import datetime
import uuid

sql_region = "{} = '{}'".format("DEPARTAMEN", REGION[1])

# Functions
def merge_capas(path_salida, *args):
    return arcpy.Merge_management([args], os.path.join(SCRATCH, path_salida))

def copy_distritos(distritos):
    return arcpy.CopyFeatures_management(distritos, os.path.join(SCRATCH, "distritos"))

def cortar_region(feature, region):
    sql = "{} = '{}'".format("DEPNOM", region)
    mfl_region = arcpy.MakeFeatureLayer_management(departamentos, "mfl_region", sql)
    fc_region = arcpy.CopyFeatures_management(mfl_region, os.path.join(SCRATCH, "region"))
    name_uuid = uuid.uuid4().hex[:3]
    clip_region = arcpy.Clip_analysis(feature, fc_region, os.path.join(SCRATCH, "clip_region_{}".format(name_uuid)))
    return clip_region

def red_vial(via_nacional, via_departamental, via_vecinal):
    '''
    Devuelve las capas de lineas y poligonos a partir de la capa de vias con merge corregido
    '''
    mfl_vn = cortar_region(via_nacional, REGION[1])
    mfl_vd = cortar_region(via_departamental, REGION[1])
    mfl_vv = cortar_region(via_vecinal, REGION[1])
    # mfl_vl = cortar_region(via_local, REGION[1])
    vias_merge = arcpy.Merge_management([mfl_vn, mfl_vd, mfl_vv],
                                        os.path.join(SCRATCH, "vias_merge"))
    mfl_rv = arcpy.CopyFeatures_management(vias_merge, os.path.join(SCRATCH, "mfl_rv"))
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
    bf = arcpy.Buffer_analysis(in_features=mfl_rv, out_feature_class=os.path.join(SCRATCH, buffer_name),
                               buffer_distance_or_field="5 Kilometers", line_side="FULL", line_end_type="ROUND",
                               dissolve_option="NONE", dissolve_field=[], method="PLANAR")
    mfl_buffer = bf.getOutput(0)

    arcpy.AddField_management(mfl_buffer, field_area, "DOUBLE")

    # Se calcula el area del buffer 5km para read vial
    with arcpy.da.UpdateCursor(mfl_buffer, ["SHAPE@", field_area]) as cursor:
        for row in cursor:
            # area en hectareas
            area_ha = row[0].getArea("GEODESIC","HECTARES")
            row[1] = area_ha
            cursor.updateRow(row)
    del cursor
    return mfl_rv, mfl_buffer

def area_natural_protegida(red_vial_line, anp_acr, anp_def, anp_pri, anp_amr, anp_zr):
    mfl_acr = cortar_region(anp_acr, REGION[1])
    mfl_def = cortar_region(anp_def, REGION[1])
    mfl_pri = cortar_region(anp_pri, REGION[1])
    mfl_amr = cortar_region(anp_amr, REGION[1])
    mfl_zr = cortar_region(anp_zr, REGION[1])

    anp_teu = arcpy.Merge_management([mfl_acr, mfl_def, mfl_pri, mfl_amr, mfl_zr],
                                     os.path.join(SCRATCH, "anp_teu"))
    # feature_clip = cortar_region(anp_teu, REGION[1])
    fieldname1 = "anp_nomb"
    fieldname2 = "anp_cate"
    mfl_ft = arcpy.MakeFeatureLayer_management(anp_teu, "mfl_ft")
    mfl_rv = arcpy.MakeFeatureLayer_management(red_vial_line, "mfl_rv")

    intersect_out_mfl = arcpy.Intersect_analysis([mfl_ft, mfl_rv], "in_memory\\intersect_anp")

    dissol_anp = arcpy.Dissolve_management(in_features=intersect_out_mfl,
                                           out_feature_class=os.path.join(SCRATCH, "dissol_anp"), dissolve_field=["ID_RV"],
                                           statistics_fields=[[fieldname1, "MAX"], [fieldname2, "MAX"]],
                                           multi_part="MULTI_PART",
                                           unsplit_lines="DISSOLVE_LINES")

    table_anp = arcpy.TableToTable_conversion(dissol_anp, PATH_GDB, "RV_{}_ANP".format(REGION[0]))
    return table_anp

def recursos_turisticos(feature, red_vial_pol):
    sql = "DPTO = 'Amazonas'"
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

    arcpy.AddField_management(isc_fc, fieldname, "DOUBLE")

    # Se calcula el porcentaje de area de buffer_turis sobre red_vial_pol
    with arcpy.da.UpdateCursor(isc_fc, ["SHAPE@", fieldname, "AREA_B5KM"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC","HECTARES")
            row[1] = area_ha/row[2]
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

def bosque_vulnerable(feature, red_vial_pol):
    sql = "VULNERABILIDAD in ('MUY ALTO', 'ALTO', 'MEDIO')"
    mfl_bv = arcpy.MakeFeatureLayer_management(feature,"mfl_bv",sql)

    intersect_bv = arcpy.Intersect_analysis(in_features=[[red_vial_pol, ""], [mfl_bv, ""]],
                                                out_feature_class=os.path.join(SCRATCH, "intersect_bv_{}".format(REGION[0])),
                                                join_attributes="ALL",
                                                cluster_tolerance="", output_type="INPUT")
    dissol_isc_bv = arcpy.Dissolve_management(in_features=intersect_bv,
                                                out_feature_class=os.path.join(SCRATCH, "dissol_isc_bv_{}".format(REGION[0])),
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
    del cursor

    table_bv = arcpy.TableToTable_conversion(dissol_isc_bv, PATH_GDB, "RV_{}_BV".format(REGION[0]))
    return table_bv

def restauracion(feature, red_vial_pol):
    mfl_roam = arcpy.MakeFeatureLayer_management(feature,"mfl_roam")

    intersect_roam = arcpy.Intersect_analysis(in_features=[[red_vial_pol, ""], [mfl_roam, ""]],
                                                out_feature_class=os.path.join(SCRATCH, "intersect_roam_{}".format(REGION[0])),
                                                join_attributes="ALL",
                                                cluster_tolerance="", output_type="INPUT")

    dissol_isc_roam = arcpy.Dissolve_management(in_features=intersect_roam,
                                                out_feature_class=os.path.join(SCRATCH, "dissol_isc_roam_{}".format(REGION[0])),
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
    del cursor

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
    del cursor

    intersect_bs = arcpy.Intersect_analysis(in_features=[[red_vial_pol, ""], [mfl_dist, ""]],
                                            out_feature_class=os.path.join(SCRATCH, "intersect_bs"),
                                            join_attributes="ALL", cluster_tolerance="",
                                            output_type="INPUT")

    dissol_bs = arcpy.Dissolve_management(in_features=intersect_bs,
                                            out_feature_class=os.path.join(SCRATCH, "dissol_bs"),
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
    del cursor

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
    del cursor

    intersect_ea = arcpy.Intersect_analysis(in_features=[[red_vial_pol, ""], [mfl_dist, ""]],
                                            out_feature_class=os.path.join(SCRATCH, "intersect_ea"),
                                            join_attributes="ALL",
                                            cluster_tolerance="", output_type="INPUT")
    dissol_ea = arcpy.Dissolve_management(in_features=intersect_ea,
                                            out_feature_class=os.path.join(SCRATCH, "dissol_ea"),
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
    del cursor

    table_ea = arcpy.TableToTable_conversion(dissol_ea, PATH_GDB, "RV_{}_EA".format(REGION[0]))
    return table_ea

def habitante_ccpp(feature, red_vial_pol):
    sql = sql_region
    # mfl_ccpp = arcpy.MakeFeatureLayer_management(feature, "ccpp", sql)
    print(os.path.join(SCRATCH, "ccpp"))
    mfl_ccpp = arcpy.Select_analysis(feature, os.path.join(SCRATCH, "ccpp"), sql)
    arcpy.AddField_management(mfl_ccpp, "REPREPOBLA", "DOUBLE")

    with arcpy.da.UpdateCursor(mfl_ccpp, ["POB_2017","REPREPOBLA"]) as cursor:
        for x in cursor:
            x[1] = x[0] / POB_REGION
            cursor.updateRow(x)
    del cursor
    # intersect_ccpp = arcpy.Intersect_analysis(in_features=[[mfl_ccpp, ""], [red_vial_pol, ""]],
    #                                           out_feature_class=os.path.join(SCRATCH, "intersect_ccpp"))
    intersect_ccpp = arcpy.Intersect_analysis(in_features=[[mfl_ccpp, ""], [red_vial_pol, ""]],
                                              out_feature_class=os.path.join(SCRATCH, "intersect_ccpp"),
                                              join_attributes="ALL",
                                              cluster_tolerance="",
                                              output_type="INPUT")
    # intersect_ccpp = os.path.join(SCRATCH, "intersect_ccpp")
    dissol_ccpp = arcpy.Dissolve_management(in_features=intersect_ccpp,
                                            out_feature_class=os.path.join(SCRATCH, "dissol_ccpp_{}".format(REGION[0])),
                                            dissolve_field=["ID_RV"], statistics_fields=[["REPREPOBLA", "SUM"]],
                                            multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    table_ccpp = arcpy.TableToTable_conversion(dissol_ccpp, PATH_GDB, "RV_{}_CCPP".format(REGION[0]))
    return table_ccpp

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
    with arcpy.da.UpdateCursor(cob_agricola_intersect2, ["SHAPE@", "AREA_B5KM", "P_CAGRI"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC", "HECTARES")
            row[2] = area_ha / row[1]
            cursor.updateRow(row)
    del cursor
    cob_agricola_dissol = arcpy.Dissolve_management(cob_agricola_intersect2, os.path.join(SCRATCH,"cob_agricola_dissol"),
                                                    dissolve_field=["ID_RV"],
                                                    statistics_fields=[[field, "SUM"]], multi_part="MULTI_PART",
                                                    unsplit_lines="DISSOLVE_LINES")
    table_cob_agricola = arcpy.TableToTable_conversion(cob_agricola_dissol, PATH_GDB,
                                                       out_name="tb_cagri_{}".format(REGION[0]))
    return table_cob_agricola

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

    polos_intersect = arcpy.Intersect_analysis(in_features=[[cobertura_dissol, ""], [pot_product, ""], [red_vial_pol, ""]],
                                               out_feature_class=os.path.join(SCRATCH,"polos_intersect1"))
    arcpy.AddMessage("polos_intersect")
    sql_3 = "PP = 'AP-AC-FL' Or PP = 'AP-AC' Or PP = 'AP-AC'"
    field = "PNTPOLOS"
    polos_mfl = arcpy.Select_analysis(polos_intersect, os.path.join(SCRATCH, "polos_mfl"), sql_3)
    arcpy.AddField_management(polos_mfl, field, "DOUBLE")

    with arcpy.da.UpdateCursor(polos_mfl, ["SHAPE@", "AREA_B5KM", field]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC", "HECTARES")
            row[2] = area_ha / row[1]
            cursor.updateRow(row)
    del cursor

    cobertura_dissol_f = arcpy.Dissolve_management(polos_mfl, os.path.join(SCRATCH, "cobertura_dissol_f"),
                                                   dissolve_field=["ID_RV"], statistics_fields=[[field, "SUM"]],
                                                   multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    arcpy.AddMessage("cobertura_dissol_f")
    table_cob_agricola = arcpy.TableToTable_conversion(cobertura_dissol_f, PATH_GDB,
                                                       out_name="tb_polos_{}".format(REGION[0]))
    return dissol_bosque, cobertura_erase, table_cob_agricola

def zona_degradada_sin_cob_agricola(cob_agri_sinbosque, bosque_nobosque, red_vial_pol):
    erase_zd = arcpy.Erase_analysis(bosque_nobosque, cob_agri_sinbosque, os.path.join(SCRATCH, "bnb_sin_cob_agri"))
    intersect_zd = arcpy.Intersect_analysis([[erase_zd, ""], [red_vial_pol, ""]], os.path.join(SCRATCH, "zd_intersect"))
    dissol_zd = arcpy.Dissolve_management(intersect_zd, os.path.join(SCRATCH, "zd_dissol"),["ID_RV", "AREA_B5KM"],
                                          statistics_fields=[], multi_part="MULTI_PART",
                                          unsplit_lines="DISSOLVE_LINES")

    arcpy.AddField_management(dissol_zd, "AREA_GEO", "DOUBLE")
    arcpy.AddField_management(dissol_zd, "PNT_ZDEGRA_SINCAGRO", "DOUBLE")

    with arcpy.da.UpdateCursor(dissol_zd, ["SHAPE@", "AREA_GEO", "PNT_ZDEGRA_SINCAGRO", "AREA_B5KM"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC", "HECTARES")
            row[1] = area_ha
            row[2] = area_ha / row[3]
            cursor.updateRow(row)
    del cursor

    table_zd = arcpy.TableToTable_conversion(dissol_zd, PATH_GDB, "tb_{}_zd".format(REGION[0]))
    return table_zd

def dictb(f_in, tb, *args):
    """
    descripcion : funcion que agrega un campo a la capa de ingreso del tipo double
                y crea un diccionario para la tabla indicada "tb" con los campos "args"
    f_in : capa a la que se le agregaran los campos de args
    tb   : tabla ingresada para generar el diccionario
    args : nombres de campos a crear en f_in, los mismo que se usan para construir el diccionario

    output: cursor--> dicionario con key :"ID_RV" y values : args
    """
    for field in args:
        print(field)
        if field.startswith("MAX"):
            arcpy.AddField_management(f_in, field, "TEXT", "#", "#", 100)
        else:
            arcpy.AddField_management(f_in, field, "DOUBLE")

    fields = []
    idrv = "ID_RV"
    fields.append(idrv)
    fields.extend(list(args))

    sql = "{} IS NOT NULL".format(idrv)
    cursor = {x[0]: x[1:] for x in arcpy.da.SearchCursor(tb, fields, sql)}
    return cursor

def clasif(vx,v1,v2,neg=None):
    """
    descripcion: funcion que evalua un valor y devuelve su clase con respecto a dos puntos de control
    vx : valor a evaluar
    v1 : punto de control 1
    v2 : punto de control 2
    neg: parametro que evalua si se requiero considerar el negativo como clase para valores menores a cero
    """
    if neg and vx<0:
        m = "NEGATIVO"
    elif vx < v1 :
        m ="BAJO"
    elif vx >= v1 and vx <v2:
        m = "MEDIO"
    elif vx >= v2 :
        m = "ALTO"

    return m

def jointables(feature,tb1_anp,tb2_tur,tb3_zdg,tb4_res,tb5_cagr,tb6_pol,tb7_eag,tb8_brs,tb9_bvu, tb10_cpp):

    idrv = "ID_RV"
    # Se crean campos y cursor para las tablas
    # Areas naturales anp
    fanp1 = "MAX_anp_nomb"
    fanp2 = "MAX_anp_cate"
    c_anp = dictb(feature,tb1_anp, fanp1, fanp2)
    print(c_anp)
    print("c_anp")

    # Recursos turisticos turis
    ftur = "SUM_P_RECTURIS"
    c_tur = dictb(feature,tb2_tur, ftur)
    print("c_tur")

    # Zona degradad
    fzdg = "PNT_ZDEGRA_SINCAGRO"
    c_zdg = dictb(feature, tb3_zdg, fzdg)
    print("c_zdg")

    # Restauracion ROAM
    fres = "PNTROAM"
    c_res = dictb(feature, tb4_res, fres)
    print("c_res")

    # Cobertura agricola
    fcagr = "SUM_P_CAGRI"
    c_cagr = dictb(feature, tb5_cagr, fcagr)
    print("c_cagr")

    # Polos
    fpol = "SUM_PNTPOLOS"
    c_pol = dictb(feature, tb6_pol, fpol)
    print("c_pol")

    # Estadistica Agraria
    feag = "PNTESTAGRI"
    c_eag = dictb(feature, tb7_eag, feag)
    print("c_eag")

    # Brechas Sociales
    fbrs = "PNTBRECHAS"
    c_brs = dictb(feature, tb8_brs, fbrs)
    print("c_brs")

    # Bosques vulnerables
    fbvu = "PNTBV"
    c_bvu = dictb(feature, tb9_bvu, fbvu)
    print("c_bvu")

    # Habitantes por centro poblado
    fcpp = "SUM_REPREPOBLA"
    c_cpp = dictb(feature, tb10_cpp, fcpp)
    print("c_cpp")


    upd_fields = [idrv, fanp1, fanp2, ftur, fzdg, fres, fcagr, fpol, feag, fbrs, fbvu, fcpp]
    ##############  0 ,   1  ,  2   ,   3 ,  4  ,  5  ,   6  ,  7  ,  8  ,  9  ,  10 ,  11 #########

    sql = "{} IS NOT NULL".format(idrv)

    with arcpy.da.UpdateCursor(feature, upd_fields, sql) as cursor:

        for row in cursor:
            row[1] = c_anp.get(row[0])[0] if c_anp.get(row[0]) else "0"
            row[2] = c_anp.get(row[0])[1] if c_anp.get(row[0]) else "0"
            row[3] = c_tur.get(row[0])[0] if c_tur.get(row[0]) else 0
            row[4] = c_zdg.get(row[0])[0] if c_zdg.get(row[0]) else 0
            row[5] = c_res.get(row[0])[0] if c_res.get(row[0]) else 0
            row[6] = c_cagr.get(row[0])[0] if c_cagr.get(row[0]) else 0
            row[7] = c_pol.get(row[0])[0] if c_pol.get(row[0]) else 0
            row[8] = c_eag.get(row[0])[0] if c_eag.get(row[0]) else 0
            row[9] = c_brs.get(row[0])[0] if c_brs.get(row[0]) else 0
            row[10] = c_bvu.get(row[0])[0] if c_bvu.get(row[0]) else 0
            row[11] = c_cpp.get(row[0])[0] if c_cpp.get(row[0]) else 0
            cursor.updateRow(row)
    del cursor

    print("UPDATE 1 finish")

    list_fields=[
    ["LENGTH_GEO", "DOUBLE", "", "LENGTH_GEO"],                     #12
    ["EVALUACION", "DOUBLE", "", "Evauacion Final"],                #13
    ["EVACLASE", "TEXT", 10, "Clasificacion Evaluacion Final"],     #14
    ["AMBIENTAL", "DOUBLE", "", "Ambiental"],                       #15
    ["AMBCLASE", "TEXT", 10, "Evaluacion Ambiental Clasificacion"], #16
    ["ECONOMICO", "DOUBLE", "", "Economico"],                       #17
    ["ECOCLASE", "TEXT", 10, "Evaluacion Economica Clasificacion"], #18
    ["SOCIAL", "DOUBLE", "", "Social"],                             #19
    ["SOCCLASE", "TEXT", 10, "Evaluacion Social Clasificacion"]     #20
        ]
    fields_eval = [x[0] for x in list_fields]

    # Creamos los campos adicionales de análisis
    for val in list_fields:
        arcpy.AddField_management(feature,val[0], val[1], "", "", val[2], val[3])

    #Definimos la lista de campos para el proceso final de evaluacion
    eval_upd = []
    eval_upd.extend(upd_fields)
    eval_upd.extend(fields_eval)
    eval_upd.append("SHAPE@")

    print("Fields agregados")

    #Comenzamos con el actualizado final de campos
    with arcpy.da.UpdateCursor(feature, eval_upd, sql ) as cursorU:

        for i in cursorU:
            val_eval = i[3] +i[4] +i[5] +i[6] +i[7] +i[8] +i[9] -i[10] +i[11]
            cls_eval = clasif(val_eval, 2.1, 4)

            val_ambi = i[5] -i[10]+ i[4]
            cls_ambi = clasif(val_ambi, 0.3, 0.7, 'si')

            val_econ = i[3] +i[6] +i[7] + i[8]
            cls_econ = clasif(val_econ, 1.5, 2.7)

            val_soci = i[9] + i[11]
            cls_soci = clasif(val_soci, 1.5, 2.7)

            #campo area
            i[12] = i[21].getLength("GEODESIC", "KILOMETERS")
            i[13] = val_eval
            i[14] = cls_eval
            i[15] = val_ambi
            i[16] = cls_ambi
            i[17] = val_econ
            i[18] = cls_econ
            i[19] = val_soci
            i[20] = cls_soci
            cursorU.updateRow(i)
    del cursor
    arcpy.CopyFeatures_management(feature, os.path.join(PATH_GDB, "RVV_EVALUACION_{}".format(REGION[1])))
    print("UPDATE 2 finish")

def process():
    # red_vial_line = os.path.join(SCRATCH, "mfl_rv")
    # red_vial_pol = os.path.join(SCRATCH, "B5KM_RV_{}".format(REGION[0]))

    start_time = datetime.now()
    arcpy.AddMessage("El proceso inicia - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    fc_distritos = copy_distritos(distritos)
    red_vial_line, red_vial_pol = red_vial(via_nacional, via_departamental, via_vecinal)
    arcpy.AddMessage("Se generaron las redes viales (lineas y poligonos) - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    fc_cob_agricola_1 = cobertura_agricola_1(cob_agricola, fc_distritos)
    arcpy.AddMessage("Se realizo la primera parte del proceso de cobertura agricola - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    tabla_anp = area_natural_protegida(red_vial_line, anp_acr, anp_def, anp_pri, anp_amr, anp_zr)
    arcpy.AddMessage("Termino proceso de ANP - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    tabla_turis = recursos_turisticos(fc_turis, red_vial_pol)
    arcpy.AddMessage("Termino proceso de Recursos turisticos - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    tabla_bv = bosque_vulnerable(bosq_vuln, red_vial_pol)
    arcpy.AddMessage("Termino proceso de Bosques vulnerables - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    tabla_roam = restauracion(fc_roam, red_vial_pol)
    arcpy.AddMessage("Termino proceso de Restauracion - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    tabla_bs = brechas_sociales(fc_distritos, red_vial_pol, tbp_brechas)
    arcpy.AddMessage("Termino proceso de Brechas sociales - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    tabla_ea = estadistica_agraria(fc_distritos,red_vial_pol, tbp_estagr)
    arcpy.AddMessage("Termino proceso de Estadistica agraria - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    tabla_cob_agric = cobertura_agricola_2(fc_cob_agricola_1, red_vial_pol)
    arcpy.AddMessage("Termino proceso de Cobertura agricola - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    cob_agri_sinbosque, bosque_nobosque, tabla_polos = polos_intensificacion(bosque, fc_cob_agricola_1, red_vial_pol)
    arcpy.AddMessage("Termino proceso de Polos - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    tabla_zd = zona_degradada_sin_cob_agricola(cob_agri_sinbosque, bosque_nobosque, red_vial_pol)
    arcpy.AddMessage("Termino Zonas degradadas - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    tabla_ccpp = habitante_ccpp(ccpp, red_vial_pol)
    arcpy.AddMessage("Termino el proceso de habitantes - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    # tabla_anp = os.path.join(PATH_GDB, "RV_{}_ANP".format(REGION[0]))
    # tabla_turis = os.path.join(PATH_GDB, "RV_{}_TUR".format(REGION[0]))
    # tabla_zd = os.path.join(PATH_GDB, "tb_{}_zd".format(REGION[0]))
    # tabla_roam = os.path.join(PATH_GDB, "RV_{}_ROAM".format(REGION[0]))
    # tabla_cob_agric = os.path.join(PATH_GDB, "tb_cagri_{}".format(REGION[0]))
    # tabla_polos = os.path.join(PATH_GDB, "tb_polos_{}".format(REGION[0]))
    # tabla_ea = os.path.join(PATH_GDB, "RV_{}_EA".format(REGION[0]))
    # tabla_bs = os.path.join(PATH_GDB, "RV_{}_BS".format(REGION[0]))
    # tabla_bv = os.path.join(PATH_GDB, "RV_{}_BV".format(REGION[0]))
    # tabla_ccpp = os.path.join(PATH_GDB, "RV_{}_CCPP".format(REGION[0]))

    jointables(red_vial_line, tabla_anp, tabla_turis, tabla_zd, tabla_roam, tabla_cob_agric, tabla_polos, tabla_ea, tabla_bs, tabla_bv, tabla_ccpp)

    end_time = datetime.now()
    arcpy.AddMessage("El proceso finaliza - {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    arcpy.AddMessage('Duracion: {}'.format(end_time - start_time))

def main():
    process()

if __name__ == '__main__':
    main()
