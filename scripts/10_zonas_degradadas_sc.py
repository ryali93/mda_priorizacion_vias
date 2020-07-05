# -*- coding: utf-8 -*-
from settings import *
from funciones import *

mod_geom = "cf" # Calculatefield

def zona_degradada_sin_cob_agricola(cob_agri_sinbosque, bosque_nobosque, red_vial_pol):
    erase_zd = arcpy.Erase_analysis(bosque_nobosque, cob_agri_sinbosque, os.path.join(SCRATCH, "bnb_sin_cob_agri"))
    intersect_zd = arcpy.Intersect_analysis([[erase_zd, ""], [red_vial_pol, ""]], os.path.join(SCRATCH, "zd_intersect"))
    dissol_zd = arcpy.Dissolve_management(intersect_zd, os.path.join(SCRATCH, "zd_dissol"),["ID_RV", "AREA_B5KM"],
                                          statistics_fields=[], multi_part="MULTI_PART",
                                          unsplit_lines="DISSOLVE_LINES")

    arcpy.AddField_management(dissol_zd, "AREA_GEO", "DOUBLE")
    arcpy.AddField_management(dissol_zd, "PNT_ZDEGRA_SINCAGRO", "DOUBLE")
    if mod_geom == 'cf':
        arcpy.CalculateField_management(dissol_zd, "AREA_GEO", "!shape.area@hectares!","PYTHON_9.3")
    with arcpy.da.UpdateCursor(dissol_zd, ["SHAPE@", "AREA_GEO", "PNT_ZDEGRA_SINCAGRO", "AREA_B5KM"]) as cursor:
        for row in cursor:
            if mod_geom == 'cf':
                area_ha = row[1]
            else:
                area_ha = row[0].getArea("GEODESIC", "HECTARES")
                row[1] = area_ha
            row[2] = area_ha / row[3]
            cursor.updateRow(row)
    del cursor

    table_zd = arcpy.TableToTable_conversion(dissol_zd, PATH_GDB, "tb_{}_zd".format(REGION[0]))
    return table_zd


def process():
    red_vial_pol = arcpy.GetParameterAsText(2)
    cob_agri_sinbosque = arcpy.GetParameterAsText(3)
    bosque_nobosque = arcpy.GetParameterAsText(4)

    tabla_zd = zona_degradada_sin_cob_agricola(cob_agri_sinbosque, bosque_nobosque, red_vial_pol)
    arcpy.AddMessage("Termino Zonas degradadas")
    arcpy.SetParameterAsText(5, tabla_zd)

def main():
    process()

if __name__ == '__main__':
    main()
