# -*- coding: utf-8 -*-
from settings import *
from funciones import *

sql_region = "{} = '{}'".format("DEPARTAMEN", REGION[1])
mod_geom = "cf" # Calculatefield
# mod_geom = "uc" # UpdateCursor

def red_vial(via_nacional, via_departamental, via_vecinal):
    '''
    Devuelve las capas de lineas y poligonos a partir de la capa de vias con merge corregido
    '''
    id_dep = REGION[0]
    mfl_vn = cortar_region(via_nacional, REGION[1])
    mfl_vd = cortar_region(via_departamental, REGION[1])
    mfl_vv = cortar_region(via_vecinal, REGION[1])
    # mfl_vl = cortar_region(via_local, REGION[1])
    vias_merge = arcpy.Merge_management([mfl_vn, mfl_vd, mfl_vv], os.path.join(SCRATCH, "vias_merge"))
    vias_clip = arcpy.Intersect_analysis([vias_merge, distritos], os.path.join(SCRATCH, "vias_clip"), 'ALL', '#', 'INPUT')
    mfl_rv = arcpy.CopyFeatures_management(vias_clip, os.path.join(PATH_GDB, "PL_RV_{}".format(id_dep)))
    desc = arcpy.Describe(mfl_rv)

    fieldname = "ID_RV"
    field_area = "AREA_B5KM"
    oidname = desc.OIDFieldName
    arcpy.AddField_management(mfl_rv, fieldname, "TEXT", "", "", 25)

    # Se crea el identificador unico para red vial
    with arcpy.da.UpdateCursor(mfl_rv, [oidname, fieldname]) as cursor:
        for row in cursor:
            row[1] = str(id_dep) + "_" + str(row[0])
            cursor.updateRow(row)
    del cursor
    bf = arcpy.Buffer_analysis(in_features=mfl_rv, out_feature_class=os.path.join(PATH_GDB, 'B5KM_RV_{}'.format(id_dep)), #
                               buffer_distance_or_field="5 Kilometers", line_side="FULL", line_end_type="ROUND",
                               dissolve_option="NONE", dissolve_field=[], method="PLANAR")
    mfl_buffer = bf.getOutput(0)

    arcpy.AddField_management(mfl_buffer, field_area, "DOUBLE")

    if mod_geom == 'cf':
        arcpy.CalculateField_management(mfl_buffer, field_area, "!shape.area@hectares!","PYTHON_9.3")
    else:
        with arcpy.da.UpdateCursor(mfl_buffer, ["SHAPE@", field_area]) as cursor:
            for row in cursor:
                area_ha = row[0].getArea("GEODESIC","HECTARES")
                row[1] = area_ha
                cursor.updateRow(row)
        del cursor
    return mfl_rv, mfl_buffer

def process():
    via_vecinal = arcpy.GetParameterAsText(2)
    via_nacional = arcpy.GetParameterAsText(3)
    via_departamental = arcpy.GetParameterAsText(4)

    red_vial_line, red_vial_pol = red_vial(via_vecinal, via_nacional, via_departamental)
    arcpy.AddMessage("Se generaron las redes viales (lineas y poligonos)")
    arcpy.SetParameterAsText(5, red_vial_line)
    arcpy.SetParameterAsText(6, red_vial_pol)

def main():
    process()

if __name__ == '__main__':
    main()