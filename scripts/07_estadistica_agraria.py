# -*- coding: utf-8 -*-
from settings import *
from funciones import *

mod_geom = "cf" # Calculatefield

def estadistica_agraria(distritos, red_vial_pol, tbpuntaje):

    mfl_dist = arcpy.MakeFeatureLayer_management(distritos,"mfl_dist")

    ubigeo = "UBIGEO"
    estad_agr = "P_ESTAD"

    arcpy.AddField_management(mfl_dist, estad_agr , "TEXT","", "", 125)

    filtro = "UBIGEO is not NULL"

    df_estad_agr = {str(int(x[0])).zfill(6):x[1] for x in arcpy.da.SearchCursor(tbpuntaje,[ubigeo, estad_agr], filtro)}

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
    if mod_geom == 'cf':
        arcpy.CalculateField_management(dissol_ea, "AREA_GEO", "!shape.area@hectares!","PYTHON_9.3")
    with arcpy.da.UpdateCursor(dissol_ea, ["SHAPE@","AREA_GEO","PNTESTAGRI","AREA_B5KM"]) as cursor:
        for row in cursor:
            if mod_geom == 'cf':
                area_ha = row[1]
            else:
                area_ha = row[0].getArea("GEODESIC","HECTARES")
                row[1] = area_ha
            row[2] = area_ha/row[3]
            cursor.updateRow(row)
    del cursor

    table_ea = arcpy.TableToTable_conversion(dissol_ea, PATH_GDB, "RV_{}_EA".format(REGION[0]))
    return table_ea

def process():
    red_vial_pol = arcpy.GetParameterAsText(2)
    fc_distritos = copy_distritos(distritos)
    tabla_ea = estadistica_agraria(fc_distritos, red_vial_pol, tbp_estagr)
    arcpy.AddMessage("Termino proceso de Estadistica agraria")
    arcpy.SetParameterAsText(3, tabla_ea)

def main():
    process()

if __name__ == '__main__':
    main()

