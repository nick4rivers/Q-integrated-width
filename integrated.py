
import os
import sys
from osgeo import ogr
from PyQt5.QtWidgets import QFileDialog
from qgis.utils import iface
from qgis.PyQt.QtCore import QVariant

from qgis.core import(
    QgsField,
    QgsVectorDataProvider,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsVectorFileWriter,
    QgsProject,
    Qgis,
    edit)

from qgis import processing

# ---- input data -----
# This should be a geopackage with two features/tables
# 1. A centerline named 'centerline'
# 2. a segmented polygon named 'valley-bottom-segmented'

# This will obviously change in the future but fine for development purposes


# Point to a geopackage
input_path = QFileDialog.getOpenFileName()[0]

# check if it is a valid file path
if not os.path.isfile(input_path):
    the_message = 'Rerun the script and choose a valid file path'
    iface.messageBar().pushMessage("Oops", the_message, level=Qgis.Critical)
    # TODO break this if it isn't a valid path        

# TODO check if it is a geopackage
    
# Open the geopackage
input_layers = ogr.Open(str(input_path))

# TODO create file dialogs asking for the name of each type

# Print a list of the tables in the geopackage
for l in input_layers:
    print(l.GetName())

# TODO #1 check validity and for empty feature classes.
# Open the valley bottom segments
raw_segments = iface.addVectorLayer(input_path + "|layername=valley-bottom-segmented", "valley-bottom-segmented", 'ogr')

# Open the centerline
raw_centerline = iface.addVectorLayer(input_path + "|layername=centerline", "centerline", 'ogr')

# TODO #2 Check what happens if layers are in different projections?

# TODO #3 What happens if centerline doesn't intersect polygons'

# TODO #4 What if the int_width_m field doesn't exist'

# TODO #5 Can we calculate widths for multiple centerlines

# TODO #6 What happens with multiple centerlines?

# TODO #7 What happens at top and bottom of reach if the centerline starts or ends partially inside the top or bottom most segment of the channel?

# TODO #8 What happens if the polygon has a donut in it?

# TODO #9 What happens if the centerline (erroneously) passes outside part of the polygon and re-enters, producing two segments that intersect the polygon?


# ------- Input Segments and Get Areas --------


# Create a data provider and string of capabilities
pr_raw_segments = raw_segments.dataProvider()
caps_raw_segments = pr_raw_segments.capabilitiesString()

# -- Calculate Area of Segments --

# add the area attribute if it doesn't exist
if "Add Attributes" in caps_raw_segments:
    if 'area_m' not in raw_segments.fields().names():
        pr_raw_segments.addAttributes([QgsField('area_m', QVariant.Int)])
    if 'int_width_m' not in raw_segments.fields().names():
        pr_raw_segments.addAttributes([QgsField('int_width_m', QVariant.Int)])
    raw_segments.updateFields()

# Create a context and scope
context = QgsExpressionContext()
context.appendScopes(
    QgsExpressionContextUtils.globalProjectLayerScopes(raw_segments))

# Loop through and add the areas
with edit(raw_segments):
    # loop them
    for f in raw_segments.getFeatures():
        context.setFeature(f)
        f['area_m'] = QgsExpression('$area').evaluate(context)
        raw_segments.updateFeature(f)


# ------- Centerline Processing --------

# Intersection tool to segment the centerline
gp_intersect = processing.run("native:intersection",
                              {'INPUT': raw_centerline,
                               'OVERLAY': raw_segments,
                               'INPUT_FIELDS': [],
                                'OVERLAY_FIELDS': [],
                                'OVERLAY_FIELDS_PREFIX': 'seg_',
                                'OUTPUT': 'TEMPORARY_OUTPUT'})

# Grab the output vector layer
temp_centerline_segmented = gp_intersect['OUTPUT']

# Add temporary to the interface
QgsProject.instance().addMapLayer(temp_centerline_segmented)


# - Calculate centerline lengths -
# Create a data provider and string of capabilities
pr_temp_centerline_segmented = temp_centerline_segmented.dataProvider()
caps_temp_centerline_segmented = pr_temp_centerline_segmented.capabilitiesString()

# add the line attribute
if "Add Attributes" in caps_temp_centerline_segmented:
    if 'length_m' not in temp_centerline_segmented.fields().names():
        pr_temp_centerline_segmented.addAttributes([QgsField('length_m', QVariant.Int)])
    if 'int_width_m' not in temp_centerline_segmented.fields().names():
        pr_temp_centerline_segmented.addAttributes([QgsField('int_width_m', QVariant.Int)])
    temp_centerline_segmented.updateFields()

# and the line length
context = QgsExpressionContext()
context.appendScopes(
    QgsExpressionContextUtils.globalProjectLayerScopes(temp_centerline_segmented))

# Loop through and add the areas and calculate widths
with edit(temp_centerline_segmented):
    # loop them
    for f in temp_centerline_segmented.getFeatures():
        context.setFeature(f)
        f['fid'] = QgsExpression('$id').evaluate(context)
        f['length_m'] = QgsExpression('$length').evaluate(context)
        f['int_width_m'] = QgsExpression('"seg_area_m" / "length_m"').evaluate(context)
        temp_centerline_segmented.updateFeature(f)


# ----- OUTPUT FINAL DATA --------
# Select a working directory
message_text = 'Select a working directory when prompted'
iface.messageBar().pushMessage(message_text, duration=10)
work_path = QFileDialog.getExistingDirectory()

# Create output directory
outputs_path = os.path.join(work_path, 'outputs')
if not os.path.exists(outputs_path):
    os.mkdir(outputs_path)


# -- Write out to a final geopackage
output_vector_path = os.path.join(outputs_path, 'integrated_line.gpkg')
QgsVectorFileWriter.writeAsVectorFormat(
    temp_centerline_segmented, output_vector_path, 'utf-8,', driverName='GPKG')


# add to the interface
iface.addVectorLayer(output_vector_path, '', 'ogr')
