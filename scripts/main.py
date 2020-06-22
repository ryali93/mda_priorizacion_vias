from settings import *

REGION = REGIONES[22]
id_region = REGION[0]
sql = "{} = '{}'".format("DEPARTAMEN", REGION[1])

# Functions
def red_vial():
    arcpy.SelectLayerByAttribute_management(via_nacional, "NEW_SELECTION", sql)
    arcpy.SelectLayerByAttribute_management(via_departamental, "NEW_SELECTION", sql)
    arcpy.SelectLayerByAttribute_management(via_vecinal, "NEW_SELECTION", sql)
    red_vial_feature = arcpy.Merge_management([via_nacional, via_departamental, via_vecinal], "in_memory\\via_merge")
    return red_vial_feature

def get_blayers(rv_feature):
    rv_dep = arcpy.MakeFeatureLayer_management(rv_feature, 'rv_dep')
    desc = arcpy.Describe(rv_dep)
    id_dep = REGION[0]
    fieldname = "ID_RV"
    oidname = desc.OIDFieldName
    arcpy.AddField_management(rv_dep, fieldname, "TEXT", "", "", 25)

    # Se crea el identificador unico para red vial
    with arcpy.da.UpdateCursor(rv_dep, [oidname, fieldname]) as cursor:
        for row in cursor:
            row[1] = id_dep + "_" + row[0]
            cursor.updateRow(row)

    bfname = 'B5KM_RV_{}'.format(id_dep)

    bf = arcpy.Buffer_analysis(in_features=rv_dep, out_feature_class='in_memory\\{}'.format(bfname), 
        buffer_distance_or_field="5 Kilometers", line_side="FULL", line_end_type="ROUND", 
        dissolve_option="NONE", dissolve_field=[], method="PLANAR")
    bf_fc = bf.getOutput(0)

    bflayer = arcpy.MakeFeatureLayer_management(bf_fc, bfname)

    field_area = "AREA_B5KM"

    arcpy.AddField_management(bflayer, field_area, "DOUBLE")

    # Se calcula el area del buffer 5km para read vial
    with arcpy.da.UpdateCursor(bflayer, ["@SHAPE", field_area]) as cursor:
        for row in cursor:
            # area en hectareas
            hec_area = row[0].getArea("GEODESIC","HECTARES")
            row[1] = hec_area
            cursor.updateRow(row)

    return rv_dep, bflayer


def area_natural_protegida(feature, red_vial_line, table_out):
    mfl_ft = arcpy.MakeFeatureLayer_management(feature, "mfl_ft")
    mfl_rv = arcpy.MakeFeatureLayer_management(red_vial_line, "mfl_rv")
    intersect_out_mfl = arcpy.Intersect_analysis([mfl_ft, mfl_rv], "intersect_anp")
    dissol_anp = arcpy.Dissolve_management(in_features=intersect_out_mfl,
                                           out_feature_class="in_memory\\dissol_anp", dissolve_field=["ID_RV"],
                                           statistics_fields=[["ANPC_NOMB", "MAX"], ["ANPC_CAT", "MAX"]],
                                           multi_part="MULTI_PART",
                                           unsplit_lines="DISSOLVE_LINES")
    table_anp = arcpy.TableToTable_conversion(dissol_anp, table_out, "RV_{}_ANP".format(REGION[0]))
    return table_anp

def recursos_turisticos(feature, red_vial_pol, table_out):
    bfname = "B10KM_RECTURIS"
    bf = arcpy.Buffer_analysis(in_features=feature, out_feature_class='in_memory\\{}'.format(bfname), 
        buffer_distance_or_field="10 Kilometers", line_side="FULL", line_end_type="ROUND", 
        dissolve_option="NONE", dissolve_field=[], method="PLANAR")
    bf10_fc = bf.getOutput(0)

    dissol_recturis = arcpy.Dissolve_management(in_features=bf10_fc, 
                                                out_feature_class='in_memory\\dissol_recturis', 
                                                dissolve_field=[],
                                                statistics_fields=[], multi_part="MULTI_PART", 
                                                unsplit_lines="DISSOLVE_LINES")
    iscname = "B10ISC_RECTURIS"
    intersect_recturis = arcpy.Intersect_analysis(in_features=[[dissol_recturis, ""], [red_vial_pol, ""]],
                                                out_feature_class='in_memory\\{}'.format(iscname), 
                                                join_attributes="ALL", 
                                                cluster_tolerance="", output_type="INPUT")
    isc_fc = intersect_recturis.getOutput(0)

    fieldname = "P_RECTURIS"
    arcpy.AddField_management(isc_fc, fieldname, "DOUBLE")

    #Se calcula el porcentaje de area de recturis sobre bf5km
    with arcpy.da.UpdateCursor(bflayer, ["@SHAPE", field_area, "AREA_B5KM"]) as cursor:
        for row in cursor:
            # area en hectareas
            hec_area = row[0].getArea("GEODESIC","HECTARES")
            row[1] = hec_area/row[2]
            cursor.updateRow(row)

    dissol_isc_rectur = arcpy.Dissolve_management(in_features=isc_fc, 
                                                out_feature_class='in_memory\\dissol_isc_rectur' ,
                                                dissolve_field=["ID_RV"], 
                                                statistics_fields=[["P_RECTURIS", "SUM"]], 
                                                multi_part="MULTI_PART", 
                                                unsplit_lines="DISSOLVE_LINES")


    table_tur = arcpy.TableToTable_conversion(dissol_isc_rectur, table_out, "RV_{}_TUR".format(REGION[0]))
    return table_tur




def habitante_ccpp(feature, red_vial_pol, table_out):
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
    table_ccpp = arcpy.TableToTable_conversion(in_rows=dissol_ccpp, out_path=table_out,
                                               out_name="RV_{}_CCPP".format(REGION[0]))
    return table_ccpp

def polos_intensificacion():
    Bosque_No_Bosque_2018_Vector_shp = "OneDrive\\SIG\\GEOBOSQUES\\2018\\Bosque_No_Bosque_2018_Vector\\Bosque_No_Bosque_2018_Vector.shp"
    BNB2018_SM = "Documents\\ArcGIS\\Projects\\Priorizacion de vias\\Priorizacion de vias.gdb\\BNB2018_SM"
    arcpy.CopyFeatures_management(in_features=Bosque_No_Bosque_2018_Vector_shp, out_feature_class=BNB2018_SM,
                                  config_keyword="", spatial_grid_1=None, spatial_grid_2=None, spatial_grid_3=None)

def process():
    red_vial_feature, red_vial_pol = red_vial()
    tabla_anp = area_natural_protegida(anp_teu, red_vial_feature, tb_anp)
    tabla_ccpp = habitante_ccpp(ccpp, red_vial_pol, tb_ccpp)

def main():
    process()
