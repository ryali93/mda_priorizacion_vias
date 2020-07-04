# -*- coding: utf-8 -*-
from settings import *
from funciones import *

sql_region = "{} = '{}'".format("DEPARTAMEN", REGION[1])
mod_geom = "cf" # Calculatefield

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
    intersect_ccpp = arcpy.Intersect_analysis(in_features=[mfl_ccpp, red_vial_pol],
                                              out_feature_class=os.path.join(SCRATCH, "intersect_ccpp_{}".format(REGION[0])))
    # --------------------------------------
    # intersect_ccpp = arcpy.Intersect_analysis(
    #     in_features=["C:\\Users\\Jerzy Virhuez\\AppData\\Local\\Temp\\scratch.gdb\\ccpp",
    #                  "C:\\Users\\Jerzy Virhuez\\AppData\\Local\\Temp\\scratch.gdb\\B5KM_RV_UCA"],
    #     out_feature_class="C:\\Users\\Jerzy Virhuez\\AppData\\Local\\Temp\\scratch.gdb\\intersect_ccpp_UCA")
    # ---------------------------------------------------------
    intersect_ccpp = os.path.join(SCRATCH, "intersect_ccpp_{}".format(REGION[0]))
    dissol_ccpp = arcpy.Dissolve_management(in_features=intersect_ccpp,
                                            out_feature_class=os.path.join(SCRATCH, "dissol_ccpp_{}".format(REGION[0])),
                                            dissolve_field=["ID_RV"], statistics_fields=[["REPREPOBLA", "SUM"]],
                                            multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
    table_ccpp = arcpy.TableToTable_conversion(dissol_ccpp, PATH_GDB, "RV_{}_CCPP".format(REGION[0]))
    return table_ccpp

def process():
    red_vial_pol = arcpy.GetParameterAsText(2)
    tabla_ccpp = habitante_ccpp(ccpp, red_vial_pol)
    arcpy.AddMessage("Termino el proceso de habitantes")
    arcpy.SetParameterAsText(3, tabla_ccpp)

def main():
    process()

if __name__ == '__main__':
    main()
