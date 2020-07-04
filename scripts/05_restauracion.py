# -*- coding: utf-8 -*-
from settings import *
from funciones import *

mod_geom = "cf" # Calculatefield

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
    if mod_geom == 'cf':
        arcpy.CalculateField_management(dissol_isc_roam, "AREA_GEO", "!shape.area@hectares!","PYTHON_9.3")
    with arcpy.da.UpdateCursor(dissol_isc_roam, ["SHAPE@","AREA_GEO","PNTROAM","AREA_B5KM"]) as cursor:
        for row in cursor:
            if mod_geom == 'cf':
                area_ha = row[1]
            else :
                area_ha = row[0].getArea("GEODESIC","HECTARES")
                row[1] = area_ha
            row[2] = area_ha/row[3]
            cursor.updateRow(row)
    del cursor

    table_roam = arcpy.TableToTable_conversion(dissol_isc_roam, PATH_GDB, "RV_{}_ROAM".format(REGION[0]))
    return table_roam

def process():
    red_vial_pol = arcpy.GetParameterAsText(2)
    tabla_roam = restauracion(fc_roam, red_vial_pol)
    arcpy.AddMessage("Termino proceso de Restauracion")

    arcpy.SetParameterAsText(3, tabla_roam)

def main():
    process()

if __name__ == '__main__':
    main()
