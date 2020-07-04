import arcpy
import os

arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "100%"

SCRATCH = arcpy.env.scratchGDB
sql = "{} = '{}'".format("DEPARTAMEN", "SAN MARTIN")
feature = r"E:\2020\mda\ccpp.shp"
red_vial_pol = os.path.join(SCRATCH, "B5KM_RV_SM")

mfl_ccpp = arcpy.Select_analysis(feature, os.path.join(SCRATCH, "ccpp"), sql)
intersect_ccpp = arcpy.Intersect_analysis(in_features=[[mfl_ccpp, ""], [red_vial_pol, ""]],
                                              out_feature_class=os.path.join(SCRATCH, "intersect_ccpp"),
                                              join_attributes="ALL",
                                              cluster_tolerance="", output_type="INPUT")