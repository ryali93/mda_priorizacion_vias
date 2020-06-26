import arcpy

fieldname = "P_RECTURIS"
dissol_isc_rectur = arcpy.Dissolve_management(in_features=r'C:\Users\ryali93\AppData\Local\Temp\scratch.gdb\intersect_turis_SM',
                                                  out_feature_class=r'C:\Users\ryali93\AppData\Local\Temp\scratch.gdb\dissol_isc_rectur_SM2',
                                                  dissolve_field=["ID_RV"],
                                                  statistics_fields=[[fieldname, "SUM"]],
                                                  multi_part="MULTI_PART",
                                                  unsplit_lines="DISSOLVE_LINES")