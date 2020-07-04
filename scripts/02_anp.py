# -*- coding: utf-8 -*-
from settings import *
from funciones import *

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

def process():
    red_vial_line = arcpy.GetParameterAsText(2)
    tabla_anp = area_natural_protegida(red_vial_line, anp_acr, anp_def, anp_pri, anp_amr, anp_zr)
    arcpy.AddMessage("Termino proceso de ANP")
    arcpy.SetParameterAsText(3, tabla_anp)

def main():
    process()

if __name__ == '__main__':
    main()