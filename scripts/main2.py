# -*- coding: utf-8 -*-
from model import *
from settings2 import *
from datetime import datetime
import time

def create_gdb(folder, region):
    fecha = time.strftime('%d%b%y')
    hora = time.strftime('%H%M%S')
    nameFile = "PROCESS-{}-{}".format(fecha, hora)
    if not os.path.exists(r'C:\mda_tmp'):
        folder_gdb = arcpy.CreateFolder_management(folder, nameFile).getOutput(0)
    else:
        folder_gdb = os.path.join(folder, nameFile)
    path_gdb = arcpy.CreateFileGDB_management(folder_gdb, region, "10.0")
    return os.path.join(folder, nameFile, region + ".gdb")

def create_datasets(gdb, datasets):
    for ds in [x.split(".")[-1] for x in datasets]:
        arcpy.CreateFeatureDataset_management(gdb, ds)

def seleccionar_region(feature, cod_region, output):
    sql = "{} = '{}'".format(feature.iddpto, cod_region)
    mfl_region = arcpy.MakeFeatureLayer_management(feature.path, "mfl", sql)
    clip_region = arcpy.CopyFeatures_management(mfl_region, output)
    return clip_region

def intersect_layers(feature, area_intersect, output):
    intersect_feature = arcpy.Intersect_analysis([feature, area_intersect],
                                                 output, 'ALL', '#', 'INPUT')
    return intersect_feature

def dissolve(feature, field_dissol, statistics, output):
    dissol_feature = arcpy.Dissolve_management(in_features=feature,
                                           out_feature_class=output,
                                           dissolve_field=field_dissol,
                                           statistics_fields=statistics, # [[fieldname1, "MAX"], [fieldname2, "MAX"]]
                                           multi_part="MULTI_PART",
                                           unsplit_lines="DISSOLVE_LINES")
    return dissol_feature

def add_field(feature, field, type="DOUBLE"):
    arcpy.AddField_management(feature, field, type)

def field_join(feature_in, feature_out, field_by, fields=None):
    join_table = arcpy.JoinField_management(feature_in, feature_out, field_by, fields)
    table_join = arcpy.CopyFeatures_management(join_table, os.path.join(SCRATCH, "table_join"))
    return table_join

def calculate_area(feature, field, mod_geom="cf"):
    if mod_geom == "cf":
        arcpy.CalculateField_management(feature, field, "!shape.area@hectares!", "PYTHON3")
    else:
        with arcpy.da.UpdateCursor(feature, ["SHAPE@", field]) as cursor:
            for row in cursor:
                area_ha = row[0].getArea("GEODESIC","HECTARES")
                row[1] = area_ha
                cursor.updateRow(row)
        del cursor

def create_buffer(feature, distancia):
    return arcpy.Buffer_analysis(feature, os.path.join(SCRATCH, "BUFFER"), distancia, "FULL", "ROUND", "NONE")

def calculate_ptj(feature, field, criterio):
    with arcpy.da.UpdateCursor(feature, [field, field]) as cursor:
        for row in cursor:
            cursor.updateRow(row)
    del cursor

def area_evaluar(feature, region, tipo = "via"):
    ''' Puede ser de las vias o de centros poblados'''
    if tipo == "via":
        field_dissol = ["CODRUTA", "ID_EV"]
        statistics = [[field_dissol, "MAX"]]
        field_area = "BRV"
    else:
        field_dissol = ["CODRUTA", "ID_EV"]
        statistics = [[field_dissol, "MAX"]]
        field_area = "BRV"
    area_eval = seleccionar_region(feature.path, REGIONES[region], os.path.join(SCRATCH, "EVALUAR"))
    dissol = dissolve(area_eval, field_dissol, statistics, os.path.join(SCRATCH, "EV_DISSOL"))
    buffer_area = create_buffer(dissol, "5 kilometers")
    add_field(buffer_area, field_area)
    calculate_area(buffer_area, field_area, mod_geom="")
    return area_eval, dissol

def p01_anp(region, area_eval, output):
    field_dissol = ["ID_RV", "CODRUTA"]
    statistics = [[gpo_anp().anp_cod, "MAX"], [gpo_anp().anp_nom, "MAX"], [gpo_anp().ranp, "MAX"]]
    anp = seleccionar_region(gpo_anp().path, REGIONES[region], os.path.join(SCRATCH, "anp_{}".format(region)))
    anp_intersect = intersect_layers(anp, area_eval, os.path.join(SCRATCH, "INTERSECT"))
    anp_dissol = dissolve(anp_intersect, field_dissol, statistics, output)
    return anp_dissol

def p02_brturis(region, area_eval, feature_final, output):
    field_id = ""
    field_dissol = ""
    statistics = [[field_dissol, "MAX"]]
    field_area = ""
    field_ptj = ""
    brturis = seleccionar_region(gpo_brturis().path, REGIONES[region], os.path.join(SCRATCH, "brturis_{}".format(region)))
    brturis_intersect = intersect_layers(brturis, area_eval, os.path.join(SCRATCH, "INTERSECT"))
    brturis_dissol = dissolve(brturis_intersect, field_dissol, statistics, output)
    add_field(brturis_dissol, field_area)
    add_field(brturis_dissol, field_ptj)
    calculate_area(brturis_dissol, field_area, mod_geom="")
    calculate_ptj(brturis_dissol, field_area, "")
    table_join = field_join(brturis_dissol, feature_final, field_id, fields={})
    return table_join


def process():
    region = nom_reg
    tipo_eval = "via"
    datasets = ["process"]
    # Crear carpeta y geodatabase
    GDB_PROCESS = create_gdb(r"C:/mda_tmp", region)
    create_datasets(GDB_PROCESS, datasets)
    # AREA_EVALUAR
    if tipo_eval == "via":
        area_eval, dissol = area_evaluar(gpl_rv_teu().path, region, tipo_eval)
    else:
        area_eval, dissol = area_evaluar(gpt_ccpp().path, region, tipo_eval)
    # VARIABLES
    anp_d = p01_anp(region, area_eval, os.path.join(GDB_PROCESS, gpo_anp().name))




def main():
    process()

if __name__ == '__main__':
    main()