# -*- coding: utf-8 -*-
from settings import *

def merge_capas(path_salida, *args):
    return arcpy.Merge_management([args], os.path.join(SCRATCH, path_salida))

def copy_distritos(distritos):
    return arcpy.CopyFeatures_management(distritos, os.path.join(SCRATCH, "distritos"))

def cortar_region(feature, region):
    sql = "{} = '{}'".format("DEPNOM", region)
    mfl_region = arcpy.MakeFeatureLayer_management(departamentos, "mfl_region", sql)
    name_uuid = uuid.uuid4().hex[:3]
    clip_region = arcpy.Clip_analysis(feature, mfl_region, os.path.join(SCRATCH, "clip_{}_{}".format(REGION[0], name_uuid)))
    return clip_region

def hidefields(lyr,*args):
    """
    funcion para ocultar campos de una capa
    lyr = capa a ser procesada
    args = nombre de los campos excepcion que no se ocultaran
    output = mfl con todos los campos apagados a excepcion de 'args'
    """
    name = os.path.basename(lyr)
    desc = arcpy.Describe(lyr)
    field_info = desc.fieldInfo
    fields = [x.name for x in desc.fields]
    # List of fields to hide
    # desc.OIDFieldName is the name of the 'FID' field
    fields.remove(desc.OIDFieldName)
    # campos a mantenerse en el lyr
    if args:
        for f in args:
            fields.remove(f)
    # los campos que se ocultaran
    fieldsToHide = fields
    for i in range(0, field_info.count):
        if field_info.getFieldName(i) in fieldsToHide:
            field_info.setVisible(i, "HIDDEN")
    outlyr = arcpy.MakeFeatureLayer_management(lyr, name, "", "", field_info)
    return outlyr
