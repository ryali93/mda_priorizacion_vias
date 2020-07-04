# -*- coding: utf-8 -*-
from settings import *
from funciones import *

mod_geom = "cf" # Calculatefield

def brechas_sociales(distritos, red_vial_pol, tbpuntaje):
    mfl_dist = arcpy.MakeFeatureLayer_management(distritos,"mfl_dist")

    ubigeo = "UBIGEO"
    brecha = "PUNT_BRECHAS"
    arcpy.AddField_management(mfl_dist, brecha, "DOUBLE")

    df_brecha = {str(int(x[0])).zfill(6):x[1] for x in arcpy.da.SearchCursor(tbpuntaje, [ubigeo, brecha])}

    # Actualizamos el campo brecha con los valores de la tabla de puntaje
    with arcpy.da.UpdateCursor(mfl_dist, [ubigeo, brecha]) as cursor:
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
    if mod_geom == 'cf':
        arcpy.CalculateField_management(dissol_bs, "AREA_GEO", "!shape.area@hectares!","PYTHON_9.3")
    with arcpy.da.UpdateCursor(dissol_bs, ["SHAPE@","AREA_GEO","PNTBRECHAS","AREA_B5KM"]) as cursor:
        for row in cursor:
            if mod_geom == 'cf':
                area_ha = row[1]
            else:
                area_ha = row[0].getArea("GEODESIC","HECTARES")
                row[1] = area_ha
            row[2] = area_ha/row[3]
            cursor.updateRow(row)
    del cursor

    table_bs = arcpy.TableToTable_conversion(dissol_bs, PATH_GDB, "RV_{}_BS".format(REGION[0]))
    return table_bs

def process():
    red_vial_pol = arcpy.GetParameterAsText(2)
    fc_distritos = copy_distritos(distritos)
    tabla_bs = brechas_sociales(fc_distritos, red_vial_pol, tbp_brechas)
    arcpy.AddMessage("Termino proceso de Brechas sociales")
    arcpy.SetParameterAsText(3, tabla_bs)

def main():
    process()

if __name__ == '__main__':
    main()
