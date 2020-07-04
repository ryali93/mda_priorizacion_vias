# -*- coding: utf-8 -*-
from settings import *
from funciones import *

sql_region = "{} = '{}'".format("DEPARTAMEN", REGION[1])
mod_geom = "cf" # Calculatefield

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
    red_vial_line = arcpy.GetParameterAsText(2)

    tabla_anp = os.path.join(PATH_GDB, "RV_{}_ANP".format(REGION[0]))
    tabla_turis = os.path.join(PATH_GDB, "RV_{}_TUR".format(REGION[0]))
    tabla_zd = os.path.join(PATH_GDB, "tb_{}_zd".format(REGION[0]))
    tabla_roam = os.path.join(PATH_GDB, "RV_{}_ROAM".format(REGION[0]))
    tabla_cob_agric = os.path.join(PATH_GDB, "tb_cagri_{}".format(REGION[0]))
    tabla_polos = os.path.join(PATH_GDB, "tb_polos_{}".format(REGION[0]))
    tabla_ea = os.path.join(PATH_GDB, "RV_{}_EA".format(REGION[0]))
    tabla_bs = os.path.join(PATH_GDB, "RV_{}_BS".format(REGION[0]))
    tabla_bv = os.path.join(PATH_GDB, "RV_{}_BV".format(REGION[0]))
    tabla_ccpp = os.path.join(PATH_GDB, "RV_{}_CCPP".format(REGION[0]))

    jointables(red_vial_line, tabla_anp, tabla_turis, tabla_zd, tabla_roam, tabla_cob_agric, tabla_polos, tabla_ea,
               tabla_bs, tabla_bv, tabla_ccpp)
    arcpy.AddMessage("Termino Zonas degradadas")
    arcpy.SetParameterAsText(5, tabla_zd)


def main():
    process()


if __name__ == '__main__':
    main()

