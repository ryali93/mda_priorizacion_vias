# -*- coding: utf-8 -*-
from settings import *
from funciones import *

mod_geom = "cf" # Calculatefield

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
    if mod_geom == 'cf':
        arcpy.CalculateField_management(dissol_isc_bv, "AREA_GEO", "!shape.area@hectares!","PYTHON_9.3")
    with arcpy.da.UpdateCursor(dissol_isc_bv, ["SHAPE@","AREA_GEO","PNTBV","AREA_B5KM"]) as cursor:
        for row in cursor:
            if mod_geom == 'cf':
                area_ha = row[1]
            else :
                area_ha = row[0].getArea("GEODESIC","HECTARES")
                row[1] = area_ha
            row[2] = area_ha/row[3]
            cursor.updateRow(row)
    del cursor

    table_bv = arcpy.TableToTable_conversion(dissol_isc_bv, PATH_GDB, "RV_{}_BV".format(REGION[0]))
    return table_bv

def process():
    red_vial_pol = arcpy.GetParameterAsText(2)
    tabla_bv = bosque_vulnerable(bosq_vuln, red_vial_pol)
    arcpy.AddMessage("Termino proceso de Bosques vulnerables")
    arcpy.SetParameterAsText(3, tabla_bv)

def main():
    process()

if __name__ == '__main__':
    main()
