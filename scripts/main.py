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
            row[1] = id_dep + "_" + row[0]
            cursor.updateRow(row)
    buffer_name = 'B5KM_RV_{}'.format(id_dep)
    bf = arcpy.Buffer_analysis(in_features=mfl_rv, out_feature_class='in_memory\\{}'.format(buffer_name),
        buffer_distance_or_field="5 Kilometers", line_side="FULL", line_end_type="ROUND", 
        dissolve_option="NONE", dissolve_field=[], method="PLANAR")
    bf_fc = bf.getOutput(0)

    mfl_buffer = arcpy.MakeFeatureLayer_management(bf_fc, buffer_name)
    arcpy.AddField_management(mfl_buffer, field_area, "DOUBLE")

    # Se calcula el area del buffer 5km para read vial
    with arcpy.da.UpdateCursor(mfl_buffer, ["@SHAPE", field_area]) as cursor:
        for row in cursor:
            # area en hectareas
            area_ha = row[0].getArea("GEODESIC","HECTARES")
            row[1] = area_ha
            cursor.updateRow(row)
    return mfl_rv, mfl_buffer

def copy_distritos(distritos):
    fc_dist = arcpy.CopyFeatures_management(distritos,Distritos_copy)


def area_natural_protegida(feature, red_vial_line):
    mfl_ft = arcpy.MakeFeatureLayer_management(feature, "mfl_ft")
    mfl_rv = arcpy.MakeFeatureLayer_management(red_vial_line, "mfl_rv")
    intersect_out_mfl = arcpy.Intersect_analysis([mfl_ft, mfl_rv], "intersect_anp")
    dissol_anp = arcpy.Dissolve_management(in_features=intersect_out_mfl,
                                           out_feature_class="in_memory\\dissol_anp", dissolve_field=["ID_RV"],
                                           statistics_fields=[["ANPC_NOMB", "MAX"], ["ANPC_CAT", "MAX"]],
                                           multi_part="MULTI_PART",
                                           unsplit_lines="DISSOLVE_LINES")
    table_anp = arcpy.TableToTable_conversion(dissol_anp, PATH_GDB, "RV_{}_ANP".format(REGION[0]))
    return table_anp

def recursos_turisticos(feature, red_vial_pol):
    fieldname = "P_RECTURIS"
    buffer_turis = arcpy.Buffer_analysis(in_features=feature, out_feature_class='in_memory\\buffer_turis',
        buffer_distance_or_field="10 Kilometers", line_side="FULL", line_end_type="ROUND", 
        dissolve_option="NONE", dissolve_field=[], method="PLANAR")
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
    with arcpy.da.UpdateCursor(buffer_turis, ["@SHAPE", fieldname, "AREA_B5KM"]) as cursor:
        for row in cursor:
            area_ha = row[0].getArea("GEODESIC","HECTARES")
            row[1] = area_ha/row[2]
            cursor.updateRow(row)
    dissol_isc_rectur = arcpy.Dissolve_management(in_features=isc_fc,
                                                out_feature_class='in_memory\\dissol_isc_rectur' ,
                                                dissolve_field=["ID_RV"], 
                                                statistics_fields=[["P_RECTURIS", "SUM"]], 
                                                multi_part="MULTI_PART", 
                                                unsplit_lines="DISSOLVE_LINES")
    table_tur = arcpy.TableToTable_conversion(dissol_isc_rectur, PATH_GDB, "RV_{}_TUR".format(REGION[0]))
    return table_tur


def brechas_sociales(distritos, red_vial_pol, xlsfile):

    mfl_dist = arcpy.MakeFeatureLayer_management(distritos,"mfl_dist")

    ubigeo = "codent"
    brecha = "PUNT_BRECHAS"

    arcpy.AddField_management(mfl_dist, brecha , "TEXT","", "", 125)

    df_brecha =  pd.read_excel(xlsfile)
    # df_brecha =  pd.read_excel(xlsfile,'HOJA1')

    # Actualizamos el campo brecha con los valores del xls
    with arcpy.da.UpdateCursor(mfl_dist, [ubigeo,brecha]) as cursor:
        for row in cursor:
            respuesta = df_brecha[df_brecha[ubigeo] = row[0]][brecha]
            row[1] = respuesta.values.tolist()[0]
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

    table_bs = arcpy.TableToTable_conversion(dissol_bs, PATH_GDB, "RV_{}_BS".format(REGION[0]))
    return table_bs




def habitante_ccpp(feature, red_vial_pol):
    mfl_ccpp = arcpy.MakeFeatureLayer_management(feature, "ccpp")
    arcpy.AddField_management(mfl_ccpp, "REPREPOBLA", "DOUBLE", None, None, None, "")
    with arcpy.UpdateCursor(mfl_ccpp, ["POB__2017_","REPREPOBLA"]) as cursor:
        for x in cursor:
            x[1] = x[0] / 813381
            cursor.updateRow(x)
    intersect_out_mfl = arcpy.Intersect_analysis(in_features=[[mfl_ccpp, ""], [red_vial_pol, ""]],
                                                 out_feature_class="in_memory\\intersect_ccpp",
                                                 join_attributes="ALL")
    dissol_ccpp = arcpy.Dissolve_management(in_features=intersect_out_mfl,
                                            out_feature_class="in_memory\\dissol_ccpp",
                                            dissolve_field=["ID_RV"], statistics_fields=[["REPREPOBLA", "SUM"]],
                                            multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    table_ccpp = arcpy.TableToTable_conversion(dissol_ccpp, PATH_GDB, "RV_{}_CCPP".format(REGION[0]))
    return table_ccpp

def polos_intensificacion():
    Bosque_No_Bosque_2018_Vector_shp = "OneDrive\\SIG\\GEOBOSQUES\\2018\\Bosque_No_Bosque_2018_Vector\\Bosque_No_Bosque_2018_Vector.shp"
    BNB2018_SM = "Documents\\ArcGIS\\Projects\\Priorizacion de vias\\Priorizacion de vias.gdb\\BNB2018_SM"
    arcpy.CopyFeatures_management(in_features=Bosque_No_Bosque_2018_Vector_shp, out_feature_class=BNB2018_SM,
                                  config_keyword="", spatial_grid_1=None, spatial_grid_2=None, spatial_grid_3=None)

def process():
    copy_distritos(Distritos)
    red_vial_line, red_vial_pol = red_vial(via_merge)
    tabla_anp = area_natural_protegida(anp_teu, red_vial_line)
    tabla_turis = recursos_turisticos(fc_turis, red_vial_pol)
    tabla_bs = brechas_sociales(distritos_copy, red_vial_pol, XLS_BRSOC)
    tabla_ccpp = habitante_ccpp(ccpp, red_vial_pol)


def main():
    process()
