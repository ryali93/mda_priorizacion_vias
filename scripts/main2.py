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
    campos = [args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9]]
    with arcpy.da.UpdateCursor(feature, campos) as cursor:
        for x in cursor:
            for campo in range(10):
                if x[campo] == None:
                    x[campo] = 0
            x[10] = x[3] + x[0] + x[8] + x[5]
            x[11] = x[4] + x[1] + x[2]
            x[12] = x[6]
            x[13] = x[11]
            x[14] = x[3] + x[0] + x[8] + x[5] + x[4] + x[1] + x[2] + x[12]
            x[15] = x[14]
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

def dictb(f_in, tb, area='', *args):
    """
    descripcion : funcion que agrega un campo a la capa de ingreso del tipo double
                y crea un diccionario para la tabla indicada "tb" con los campos "args"
    f_in : capa a la que se le agregaran los campos de args
    tb   : tabla ingresada para generar el diccionario
    args : nombres de campos a crear en f_in, los mismo que se usan para construir el diccionario

    output: cursor--> dicionario con key :"ID_RV" y values : args
    """
    for field in args:
        print(field)
        if field.startswith("MAX"):
            arcpy.AddField_management(f_in, field, "TEXT", "#", "#", 100)
        else:
            arcpy.AddField_management(f_in, field, "DOUBLE")

    fields = []
    idrv = "ID_RV"
    fields.append(idrv)
    fields.extend(list(args))
    if area not in ('','#'):
        fields.append("AREA_GEO")
    sql = "{} IS NOT NULL".format(idrv)
    cursor = {x[0]: x[1:] for x in arcpy.da.SearchCursor(tb, fields, sql)}
    return cursor

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
    print("max: {} - min: {}".format(max_data, min_data))
    print("max_ret: {} - min_ret: {}".format(min_ret, max_ret))
    return min_ret, max_ret

def jointables(feature, tb1_anp, tb2_tur, tb3_zdg, tb4_res, tb5_cagr, tb6_pol, tb7_eag, tb8_brs, tb9_bvu, tb10_cpp):

    idrv = "ID_RV"
    # Se crean campos y cursor para las tablas
    # Areas naturales anp
    fanp1 = "MAX_anp_nomb"
    fanp2 = "MAX_anp_cate"
    c_anp = dictb(feature, tb1_anp,'', fanp1, fanp2)
    print(c_anp)
    print("c_anp")

    # Recursos turisticos turis
    ftur = "SUM_P_RECTURIS"
    c_tur = dictb(feature, tb2_tur, 'si', ftur)
    print("c_tur")

    # Zona degradad
    fzdg = "PNT_ZDEGRA_SINCAGRO"
    c_zdg = dictb(feature, tb3_zdg, 'si', fzdg)
    print("c_zdg")

    # Restauracion ROAM
    fres = "PNTROAM"
    c_res = dictb(feature, tb4_res, 'si', fres)
    print("c_res")

    # Cobertura agricola
    fcagr = "SUM_P_CAGRI"
    c_cagr = dictb(feature, tb5_cagr, 'si', fcagr)
    print("c_cagr")

    # Polos
    fpol = "SUM_PNTPOLOS"
    c_pol = dictb(feature, tb6_pol, 'si', fpol)
    print("c_pol")

    # Estadistica Agraria
    feag = "PNTESTAGRI"
    c_eag = dictb(feature, tb7_eag, 'si', feag)
    print("c_eag")

    # Brechas Sociales
    fbrs = "PNTBRECHAS"
    c_brs = dictb(feature, tb8_brs, 'si', fbrs)
    print("c_brs")

    # Bosques vulnerables
    fbvu = "PNTBV"
    c_bvu = dictb(feature, tb9_bvu, 'si', fbvu)
    print("c_bvu")

    # Habitantes por centro poblado
    fcpp = "SUM_REPREPOBLA"
    c_cpp = dictb(feature, tb10_cpp, '', fcpp)
    print("c_cpp")

    upd_fields = [idrv, fanp1, fanp2, ftur, fzdg, fres, fcagr, fpol, feag, fbrs, fbvu, fcpp]
    ##############  0 ,   1  ,  2   ,   3 ,  4  ,  5  ,   6  ,  7  ,  8  ,  9  ,  10 ,  11 #########

    ##### Agregamos campos de área ########

    area_fields=[
    ["AREA_TUR", "DOUBLE", "", "Area Recurso Turistico ha"],          #12
    ["AREA_ZDEGR", "DOUBLE", "", "Area Zonas Degradadas ha"],         #13
    ["AREA_ROAM", "DOUBLE", "", "Area Restauracion ha"],              #14
    ["AREA_CAGRI", "DOUBLE", "", "Area Cobertura agricola ha"],       #15
    ["AREA_POLOS", "DOUBLE", "", "Area Polos de intensificacion ha"], #16
    ["AREA_EAG", "DOUBLE", "", "Area Estadistica Agraria ha"],        #17
    ["AREA_BRS", "DOUBLE", "", "Area Brechas Sociales ha"],           #18
    ["AREA_BV", "DOUBLE", "", "Area Bosque Vulnerable ha"],           #19
        ]

    upd_area = []
    upd_area.extend(upd_fields)

    for x in area_fields:
        upd_area.append(x[0])
        arcpy.AddField_management(feature,x[0], x[1], "", "", x[2], x[3])

    sql = "{} IS NOT NULL".format(idrv)

    with arcpy.da.UpdateCursor(feature, upd_area, sql) as cursor:

        for row in cursor:
            row[1] = c_anp.get(row[0])[0] if c_anp.get(row[0]) else "0"
            row[2] = c_anp.get(row[0])[1] if c_anp.get(row[0]) else "0"
            row[3] = c_tur.get(row[0])[0] if c_tur.get(row[0]) else 0
            row[4] = c_zdg.get(row[0])[0] if c_zdg.get(row[0]) else 0
            row[5] = c_res.get(row[0])[0] if c_res.get(row[0]) else 0
            row[6] = c_cagr.get(row[0])[0] if c_cagr.get(row[0]) else 0
            row[7] = c_pol.get(row[0])[0] if c_pol.get(row[0]) else 0
            row[8] = c_eag.get(row[0])[0] if c_eag.get(row[0]) else 0
            row[9] = c_brs.get(row[0])[0] if c_brs.get(row[0]) else 0
            row[10] = c_bvu.get(row[0])[0] if c_bvu.get(row[0]) else 0
            row[11] = c_cpp.get(row[0])[0] if c_cpp.get(row[0]) else 0

            #ahora los campos de area
            row[12] = c_tur.get(row[0])[-1] if c_tur.get(row[0]) else 0
            row[13] = c_zdg.get(row[0])[-1] if c_zdg.get(row[0]) else 0
            row[14] = c_res.get(row[0])[-1] if c_res.get(row[0]) else 0
            row[15] = c_cagr.get(row[0])[-1] if c_cagr.get(row[0]) else 0
            row[16] = c_pol.get(row[0])[-1] if c_pol.get(row[0]) else 0
            row[17] = c_eag.get(row[0])[-1] if c_eag.get(row[0]) else 0
            row[18] = c_brs.get(row[0])[-1] if c_brs.get(row[0]) else 0
            row[19] = c_bvu.get(row[0])[-1] if c_bvu.get(row[0]) else 0
            cursor.updateRow(row)
    del cursor

    print("UPDATE 1 finish")

    list_fields=[
    ["LENGTH_GEO", "DOUBLE", "", "LENGTH_GEO"],                     #12
    ["EVALUACION", "DOUBLE", "", "Evaluacion Final"],                #13
    ["EVACLASE", "TEXT", 10, "Clasificacion Evaluacion Final"],     #14
    ["AMBIENTAL", "DOUBLE", "", "Ambiental"],                       #15
    ["AMBCLASE", "TEXT", 10, "Evaluacion Ambiental Clasificacion"], #16
    ["ECONOMICO", "DOUBLE", "", "Economico"],                       #17
    ["ECOCLASE", "TEXT", 10, "Evaluacion Economica Clasificacion"], #18
    ["SOCIAL", "DOUBLE", "", "Social"],                             #19
    ["SOCCLASE", "TEXT", 10, "Evaluacion Social Clasificacion"]     #20
        ]
    fields_eval = [x[0] for x in list_fields]

    # Creamos los campos adicionales de análisis
    for val in list_fields:
        arcpy.AddField_management(feature, val[0], val[1], "", "", val[2], val[3])

    # Definimos la lista de campos para el proceso final de evaluacion
    eval_upd = []
    eval_upd.extend(upd_fields)
    eval_upd.extend(fields_eval)
    eval_upd.append("SHAPE@")

    print("Fields agregados")

    list_val_eval = []
    list_val_ambi = []
    list_val_econ = []
    list_val_soci = []

    with arcpy.da.SearchCursor(feature, eval_upd, sql) as cursor:
        for i in cursor:
            val_eval = i[3] + i[4] + i[5] + i[6] + i[7] + i[8] + i[9] - i[10] + i[11]
            list_val_eval.append(val_eval)

            val_ambi = i[5] - i[10] + i[4]
            list_val_ambi.append(val_ambi)

            val_econ = i[3] + i[6] + i[7] + i[8]
            list_val_econ.append(val_econ)

            val_soci = i[9] + i[11]
            list_val_soci.append(val_soci)

    del cursor

    bp_eval_min, bp_eval_max = max_min_data(list_val_eval)
    bp_ambi_min, bp_ambi_max = max_min_data(list_val_ambi)
    bp_econ_min, bp_econ_max = max_min_data(list_val_econ)
    bp_soci_min, bp_soci_max = max_min_data(list_val_soci)

    # Comenzamos con el actualizado final de campos
    with arcpy.da.UpdateCursor(feature, eval_upd, sql) as cursorU:

        for i in cursorU:
            val_eval = i[3] + i[4] + i[5] + i[6] + i[7] + i[8] + i[9] - i[10] + i[11]
            cls_eval = clasif(val_eval, bp_eval_min, bp_eval_max)

            val_ambi = i[5] - i[10] + i[4]
            cls_ambi = clasif(val_ambi, bp_ambi_min, bp_ambi_max)

            val_econ = i[3] + i[6] + i[7] + i[8]
            cls_econ = clasif(val_econ, bp_econ_min, bp_econ_max)

            val_soci = i[9] + i[11]
            cls_soci = clasif(val_soci, bp_soci_min, bp_soci_max)

            # campo area
            i[12] = i[21].getLength("GEODESIC", "KILOMETERS")
            i[13] = val_eval
            i[14] = cls_eval
            i[15] = val_ambi
            i[16] = cls_ambi
            i[17] = val_econ
            i[18] = cls_econ
            i[19] = val_soci
            i[20] = cls_soci
            cursorU.updateRow(i)
    del cursorU
    arcpy.CopyFeatures_management(feature, os.path.join(PATH_GDB, "RVV_EVALUACION_{}".format(REGION[1])))
    print("UPDATE 2 finish")


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

    # GDB_PROCESS = r"C:/mda_tmp/PROCESS_19092020_135735/UCAYALI.gdb"
    # area_eval = os.path.join(GDB_PROCESS, "area_EVALUAR")
    # dissol = os.path.join(GDB_PROCESS, "area_DISSOL")
    # buffer = os.path.join(GDB_PROCESS, "area_BUFFER")
    # VARIABLES
    tb_anp = p01_anp(region, buffer, area_eval, os.path.join(GDB_PROCESS, "tb_{}".format(gpo_anp().name)))
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
    actualizar_valor(area_eval, "P_CAGRI", "PZDEGRA", "P_RDEF", "P_RTURIS", "P_ROAM", "P_POLOS",
                     "MEDIAN_PSOCIAL", "MEDIAN_PVBPA", "SUM_POBCCPP", "PECONOMICO", "PPREAMBIENTAL",
                     "PSOCIAL", "PAMBIENTAL", "PPRETOTAL", "PTOTAL")
    actualizar_valor2(area_eval, "PAMBIENTAL", "PTOTAL")

def main():
    process()

if __name__ == '__main__':
    main()
