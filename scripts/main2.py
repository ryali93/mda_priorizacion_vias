# -*- coding: utf-8 -*-
from model import *
from settings2 import *
from datetime import datetime
import time

def create_gdb(folder, region):
    fecha = time.strftime('%d%m%Y')
    hora = time.strftime('%H%M%S')
    nameFile = "PROCESS_{}_{}".format(fecha, hora)
    if not os.path.exists(r'C:\mda_tmp'):
        os.mkdir(folder)
    if not os.path.exists(r'C:\mda_tmp\{}'.format(nameFile)):
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

def field_join(feature_in, feature_out, field_by, table_output, fields=None):
    join_table = arcpy.JoinField_management(feature_in, field_by, feature_out, field_by, fields)
    table_join = arcpy.CopyFeatures_management(join_table, table_output)
    return table_join

def calculate_area(feature, field, mod_geom="cf"):
    if mod_geom == "cf":
        arcpy.CalculateField_management(feature, field, "!shape.area@hectares!", python_version)
    else:
        with arcpy.da.UpdateCursor(feature, ["SHAPE@", field]) as cursor:
            for row in cursor:
                area_ha = row[0].getArea("GEODESIC","HECTARES")
                row[1] = area_ha
                cursor.updateRow(row)
        del cursor

def create_buffer(feature, distancia, output):
    return arcpy.Buffer_analysis(feature, output, distancia, "FULL", "ROUND", "NONE")

def calculate_ptj(feature, field_area, field_ptj):
    areas = [x[0] for x in arcpy.da.SearchCursor(feature, field_area)]
    sum_areas = sum(areas)
    with arcpy.da.UpdateCursor(feature, [field_area, field_ptj]) as cursor:
        for row in cursor:
            row[1] = row[0] / sum_areas
            cursor.updateRow(row)
    del cursor

def area_evaluar(feature, region, output_eval, output_dissol, output_buffer, tipo = "via"):
    ''' Puede ser de las vias o de centros poblados'''
    if tipo == "via":
        field_dissol = ["CODRUTA", "ID_EV"]
        statistics = "#"
        field_area = "BRV"
    else:
        field_dissol = ["CODRUTA", "ID_EV"]
        statistics = "#"
        field_area = "BRV"
    area_eval = seleccionar_region(feature, REGIONES[region][0], output_eval)
    dissol = dissolve(area_eval, field_dissol, statistics, output_dissol)
    buffer_area = create_buffer(dissol, "5 kilometers", output_buffer)
    add_field(buffer_area, field_area)
    calculate_area(buffer_area, field_area, mod_geom="cf")
    return area_eval, dissol, buffer_area

def p01_anp(region, area_eval, feature_final, table_output):
    field_id = "ID_EV"
    field_dissol = ["ID_EV", "CODRUTA"]
    statistics = [[gpo_anp().anp_cod, "MAX"], [gpo_anp().anp_nom, "MAX"], [gpo_anp().ranp, "MAX"]]
    anp = seleccionar_region(gpo_anp(), REGIONES[region][0], os.path.join(SCRATCH, "anp_{}".format(region)))
    anp_intersect = intersect_layers(anp, area_eval, os.path.join(SCRATCH, "anp_INTERSECT"))
    anp_dissol = dissolve(anp_intersect, field_dissol, statistics, os.path.join(SCRATCH, "anp_DISSOL"))
    table_join = field_join(feature_final, anp_dissol, field_id, table_output)
    return table_join

def p02_brturis(region, area_eval, feature_final, table_output):
    field_id = "ID_EV"
    field_dissol = ["ID_EV", "BRV"]
    statistics = "#"
    field_area = "A_RTURIS"
    field_ptj = "P_RTURIS"
    brturis = seleccionar_region(gpo_brturis(), REGIONES[region][0], os.path.join(SCRATCH, "brturis_{}".format(region)))
    brturis_intersect = intersect_layers(brturis, area_eval, os.path.join(SCRATCH, "brturis_INTERSECT"))
    brturis_dissol = dissolve(brturis_intersect, field_dissol, statistics, os.path.join(SCRATCH, "brturis_DISSOL"))
    add_field(brturis_dissol, field_area)
    add_field(brturis_dissol, field_ptj)
    calculate_area(brturis_dissol, field_area, mod_geom="cf")
    calculate_ptj(brturis_dissol, field_area,  field_ptj)
    table_join = field_join(feature_final, brturis_dissol, field_id, table_output)
    return table_join

def p03_cagri(region, area_eval, feature_final, table_output):
    field_id = "ID_EV"
    field_dissol = ["ID_EV", "BRV"]
    statistics = "#"
    field_area = "A_CAGRI"
    field_ptj = "P_CAGRI"
    cagri = seleccionar_region(gpo_cagri(), REGIONES[region][0], os.path.join(SCRATCH, "cagri_{}".format(region)))
    cagri_intersect = intersect_layers(cagri, area_eval, os.path.join(SCRATCH, "cagri_INTERSECT"))
    cagri_dissol = dissolve(cagri_intersect, field_dissol, statistics, os.path.join(SCRATCH, "cagri_DISSOL"))
    add_field(cagri_dissol, field_area)
    add_field(cagri_dissol, field_ptj)
    calculate_area(cagri_dissol, field_area, mod_geom="cf")
    calculate_ptj(cagri_dissol, field_area, field_ptj)
    table_join = field_join(feature_final, cagri_dissol, field_id, table_output)
    return table_join

def p04_rdef(region, area_eval, feature_final, table_output):
    field_id = "ID_EV"
    field_dissol = ["ID_EV", "BRV"]
    statistics = [["PROB", "MEAN"]] # arcgis pro: median | arcmap: mean
    field_area = "A_RDEF"
    field_ptj = "P_RDEF"
    rdef = seleccionar_region(gpo_rdef(), REGIONES[region][0], os.path.join(SCRATCH, "rdef_{}".format(region)))
    rdef_intersect = intersect_layers(rdef, area_eval, os.path.join(SCRATCH, "rdef_INTERSECT"))
    rdef_dissol = dissolve(rdef_intersect, field_dissol, statistics, os.path.join(SCRATCH, "rdef_DISSOL"))
    add_field(rdef_dissol, field_area)
    add_field(rdef_dissol, field_ptj)
    calculate_area(rdef_dissol, field_area, mod_geom="cf")
    calculate_ptj(rdef_dissol, field_area, field_ptj)
    table_join = field_join(feature_final, rdef_dissol, field_id, table_output)
    return table_join

def p05_roam(region, area_eval, feature_final, table_output):
    field_id = "ID_EV"
    field_dissol = ["ID_EV", "BRV"]
    # statistics = [[field_dissol, "MAX"]]
    statistics = "#"
    field_area = "A_ROAM"
    field_ptj = "P_ROAM"
    roam = seleccionar_region(gpo_roam(), REGIONES[region][0], os.path.join(SCRATCH, "roam_{}".format(region)))
    roam_intersect = intersect_layers(roam, area_eval, os.path.join(SCRATCH, "roam_INTERSECT"))
    roam_dissol = dissolve(roam_intersect, field_dissol, statistics, os.path.join(SCRATCH, "roam_DISSOL"))
    add_field(roam_dissol, field_area)
    add_field(roam_dissol, field_ptj)
    calculate_area(roam_dissol, field_area, mod_geom="cf")
    calculate_ptj(roam_dissol, field_area, field_ptj)
    table_join = field_join(feature_final, roam_dissol, field_id, table_output)
    return table_join

def p06_zdegra(region, area_eval, feature_final, table_otuput):
    field_id = "ID_EV"
    field_dissol = ["ID_EV", "BRV"]
    # statistics = [[field_dissol, "MAX"]]
    statistics = "#"
    field_area = "A_ZDEGRA"
    field_ptj = "P_ZDEGRA"
    zdegra = seleccionar_region(gpo_zdegra(), REGIONES[region][0], os.path.join(SCRATCH, "zdegra_{}".format(region)))
    zdegra_intersect = intersect_layers(zdegra, area_eval, os.path.join(SCRATCH, "zdegra_INTERSECT"))
    zdegra_dissol = dissolve(zdegra_intersect, field_dissol, statistics, os.path.join(SCRATCH, "zdegra_DISSOL"))
    add_field(zdegra_dissol, field_area)
    add_field(zdegra_dissol, field_ptj)
    calculate_area(zdegra_dissol, field_area, mod_geom="cf")
    calculate_ptj(zdegra_dissol, field_area, field_ptj)
    table_join = field_join(feature_final, zdegra_dissol, field_id, table_otuput)
    return table_join

def p07_dist(region, area_eval, feature_final, table_output):
    field_id = "ID_EV"
    field_dissol = ["ID_EV"]
    statistics = [["PSOCIAL", "MEAN"], ["PVBPA", "MEAN"]] # arcgis pro: median | arcmap: mean
    dist = seleccionar_region(gpo_limitedistrital(), REGIONES[region][0], os.path.join(SCRATCH, "dist_{}".format(region)))
    dist_intersect = intersect_layers(dist, area_eval, os.path.join(SCRATCH, "dist_INTERSECT"))
    dist_dissol = dissolve(dist_intersect, field_dissol, statistics, os.path.join(SCRATCH, "dist_DISSOL"))
    table_join = field_join(feature_final, dist_dissol, field_id, table_output)
    return table_join

def p08_ccpp(region, area_eval, feature_final, table_output):
    field_id = "ID_EV"
    field_dissol = ["ID_EV"]
    statistics = [["POBCCPP", "SUM"]]
    ccpp = seleccionar_region(gpt_ccpp(), REGIONES[region][0], os.path.join(SCRATCH, "ccpp_{}".format(region)))
    ccpp_intersect = intersect_layers(ccpp, area_eval, os.path.join(SCRATCH, "ccpp_INTERSECT"))
    ccpp_dissol = dissolve(ccpp_intersect, field_dissol, statistics, os.path.join(SCRATCH, "ccpp_DISSOL"))
    table_join = field_join(feature_final, ccpp_dissol, field_id, table_output)
    return table_join

def p09_polos(region, area_eval, feature_final, table_output):
    field_id = "ID_EV"
    field_dissol = ["BRV", "ID_EV"]
    statistics = "#"
    field_area = "A_POLOS"
    field_ptj = "P_POLOS"
    polos = seleccionar_region(gpo_polos(), REGIONES[region][0], os.path.join(SCRATCH, "polos_{}".format(region)))
    polos_intersect = intersect_layers(polos, area_eval, os.path.join(SCRATCH, "polos_INTERSECT"))
    polos_dissol = dissolve(polos_intersect, field_dissol, statistics, os.path.join(SCRATCH, "polos_DISSOL"))
    add_field(polos_dissol, field_area)
    add_field(polos_dissol, field_ptj)
    calculate_area(polos_dissol, field_area, mod_geom="cf")
    calculate_ptj(polos_dissol, field_area, field_ptj)
    table_join = field_join(feature_final, polos_dissol, field_id, table_output)
    return table_join

def agregar_campos(feature, *args):
    for field in args:
        add_field(feature, field[0], type=field[1])

def actualizar_valor(feature, *args):
    # "P_CAGRI", "PZDEGRA", "P_RDEF", "P_RTURIS", "P_ROAM", "P_POLOS", "MEDIAN_PSOCIAL", "MEDIAN_PVBPA", "SUM_POBCCPP", "PECONOMICO", "PPREAMBIENTAL", "PSOCIAL", "PAMBIENTAL", "PPRETOTAL", "PTOTAL"
    campos = [args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9], args[10],
              args[11], args[12], args[13], args[14]]
    with arcpy.da.UpdateCursor(feature, campos) as cursor:
        for x in cursor:
            for campo in range(9):
                if x[campo] == None:
                    x[campo] = 0
            x[9] = x[3] + x[0] + x[8] + x[5]
            x[10] = x[4] + x[1] + x[2]
            x[11] = x[6]
            x[12] = x[11]
            x[13] = x[3] + x[0] + x[8] + x[5] + x[4] + x[1] + x[2] + x[12]
            x[14] = x[13]
            cursor.updateRow(x)

def actualizar_valor2(feature, *args):
    campos = [args[0], args[1]]
    with arcpy.da.UpdateCursor(feature, campos) as cursor:
        for x in cursor:
            if (x[0] == None) or (x[0] < 0):
                x[0] = 0
            if (x[1] == None) or (x[1] < 0):
                x[1] = 0
            cursor.updateRow(x)

def actualizar_valor3(feature, *args):
    # "PAMBIENTAL", "PECONOMICO", "PSOCIAL", "PTOTAL", "CAMBIENTAL", "CECONOMICO", "CSOCIAL", "CTOTAL"
    campos = [args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7]]
    min_ret0, max_ret0 = max_min_data([x[0] for x in arcpy.da.SearchCursor(feature, [campos[0]])])
    min_ret1, max_ret1 = max_min_data([x[0] for x in arcpy.da.SearchCursor(feature, [campos[1]])])
    min_ret2, max_ret2 = max_min_data([x[0] for x in arcpy.da.SearchCursor(feature, [campos[2]])])
    min_ret3, max_ret3 = max_min_data([x[0] for x in arcpy.da.SearchCursor(feature, [campos[3]])])

    with arcpy.da.UpdateCursor(feature, campos) as cursor:
        for x in cursor:
            x[4] = clasif(x[0], min_ret0, max_ret0)
            x[5] = clasif(x[1], min_ret1, max_ret1)
            x[6] = clasif(x[2], min_ret2, max_ret2)
            x[7] = clasif(x[3], min_ret3, max_ret3)
            cursor.updateRow(x)

def clasif(vx,v1,v2):
    """
    descripcion: funcion que evalua un valor y devuelve su clase con respecto a dos puntos de control
    vx : valor a evaluar
    v1 : punto de control 1
    v2 : punto de control 2
    neg: parametro que evalua si se requiero considerar el negativo como clase para valores menores a cero
    """
    if vx < 0:
        m = "NEGATIVO"
    elif vx >= 0 and vx < v1:
        m = "BAJO"
    elif vx >= v1 and vx < v2:
        m = "MEDIO"
    elif vx >= v2:
        m = "ALTO"
    return m

def max_min_data(data):
    max_data = max(data)
    if min(data) >= 0:
        min_data = min(data)
    else:
        min_data = min([x for x in data if x >= 0])
    min_ret = (max_data - min_data) / 3 + min_data
    max_ret = (max_data - min_data) * 2 / 3 + min_data
    return min_ret, max_ret

def process():
    region = nom_reg
    tipo_eval = "via"
    datasets = ["process"]
    # Crear carpeta y geodatabase
    GDB_PROCESS = create_gdb(r"C:/mda_tmp", region)
    create_datasets(GDB_PROCESS, datasets)
    # AREA_EVALUAR
    if tipo_eval == "via":
        eval = gpl_rv_teu()
    else:
        eval = gpt_ccpp()
    area_eval, dissol, buffer = area_evaluar(eval, region,
                                             os.path.join(GDB_PROCESS, "area_EVALUAR"),
                                             os.path.join(GDB_PROCESS, "area_DISSOL"),
                                             os.path.join(GDB_PROCESS, "area_BUFFER"), tipo_eval)

    # GDB_PROCESS = r"C:/mda_tmp/PROCESS_19092020_182224/UCAYALI.gdb"
    # area_eval = os.path.join(GDB_PROCESS, "area_EVALUAR")
    # dissol = os.path.join(GDB_PROCESS, "area_DISSOL")
    # buffer = os.path.join(GDB_PROCESS, "area_BUFFER")
    # VARIABLES
    # tb_anp = p01_anp(region, buffer, area_eval, os.path.join(GDB_PROCESS, "tb_{}".format(gpo_anp().name)))
    print("tb_anp")
    tb_brturis = p02_brturis(region, buffer, area_eval, os.path.join(GDB_PROCESS, "tb_{}".format(gpo_brturis().name)))
    print("tb_brturis")
    tb_cagri = p03_cagri(region, buffer, area_eval, os.path.join(GDB_PROCESS, "tb_{}".format(gpo_cagri().name)))
    print("tb_cagri")
    tb_rdef = p04_rdef(region, buffer, area_eval, os.path.join(GDB_PROCESS, "tb_{}".format(gpo_rdef().name)))
    print("tb_rdef")
    tb_roam = p05_roam(region, buffer, area_eval, os.path.join(GDB_PROCESS, "tb_{}".format(gpo_roam().name)))
    print("tb_roam")
    tb_zdegra = p06_zdegra(region, buffer, area_eval, os.path.join(GDB_PROCESS, "tb_{}".format(gpo_zdegra().name)))
    print("tb_zdegra")
    tb_dist = p07_dist(region, buffer, area_eval, os.path.join(GDB_PROCESS, "tb_{}".format(gpo_limitedistrital().name)))
    print("tb_dist")
    tb_ccpp = p08_ccpp(region, buffer, area_eval, os.path.join(GDB_PROCESS, "tb_{}".format(gpt_ccpp().name)))
    print("tb_ccpp")
    tb_polos = p09_polos(region, buffer, area_eval, os.path.join(GDB_PROCESS, "tb_{}".format(gpo_polos().name)))
    print("tb_polos")
    agregar_campos(area_eval, ["PECONOMICO", "DOUBLE"], ["PSOCIAL", "DOUBLE"], ["PPREAMBIENTAL", "DOUBLE"],
                   ["PTOTAL", "DOUBLE"], ["CECONOMICO", "TEXT"], ["CSOCIAL", "TEXT"], ["CAMBIENTAL", "TEXT"],
                   ["CTOTAL", "TEXT"], ["PAMBIENTAL", "DOUBLE"], ["PPRETOTAL", "DOUBLE"])
    actualizar_valor(area_eval, "P_CAGRI", "P_ZDEGRA", "P_RDEF", "P_RTURIS", "P_ROAM", "P_POLOS",
                     "MEAN_PSOCIAL", "MEAN_PVBPA", "SUM_POBCCPP", "PECONOMICO", "PPREAMBIENTAL",
                     "PSOCIAL", "PAMBIENTAL", "PPRETOTAL", "PTOTAL") # "MEDIAN_PSOCIAL", "MEDIAN_PVBPA", "SUM_POBCCPP", "PECONOMICO", "PPREAMBIENTAL",
    actualizar_valor2(area_eval, "PAMBIENTAL", "PTOTAL")
    actualizar_valor3(area_eval, "PAMBIENTAL", "PECONOMICO", "PSOCIAL", "PTOTAL", "CAMBIENTAL", "CECONOMICO", "CSOCIAL", "CTOTAL")

def main():
    process()

if __name__ == '__main__':
    main()
