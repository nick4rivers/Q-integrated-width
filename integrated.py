
import os
from osgeo import ogr
from PyQt5.QtWidgets import QFileDialog
from qgis.utils import iface
from qgis.PyQt.QtCore import QVariant


from qgis.core import QgsField, QgsVectorDataProvider


# ---- input data -----
# This should be a geopackage with two features/tables
# 1. A centerline named 'centerline'
# 2. a segmented polygon named 'valley-bottom-segmented'

# This will obviously change in the future but fine for development purposes

# Point to a geopackage
input_path = QFileDialog.getOpenFileName()[0]

# Open the geopackage
input_layers = ogr.Open(str(input_path))

# TODO create file dialogs asking for the name of each type

# Print a list of the tables in the geopackage
for l in input_layers:
    print(l.GetName())

# Open the segments and add to variable
raw_segments = iface.addVectorLayer(input_path + "|layername=valley-bottom-segmented", "valley-bottom-segmented", 'ogr')
# TODO rename
# TODO a bit of symbology

# Open the centerline and add to variable
raw_centerline = iface.addVectorLayer(input_path + "|layername=centerline", "centerline", 'ogr')
# TODO rename
# TODO a bit of symbology

# ------- Processing --------

# Create a data provider and string of capabilities
pr = raw_segments.dataProvider()
caps = pr.capabilitiesString()

# Add areas to the segments in meters
if "Add Attributes" in caps:
    pr.addAttributes([QgsField('area_m', QVariant.Int)])
    raw_segments.updateFields()


# Calculate centerline lengths


# Divide centerline length by valley bottom area


# Attribute the centerline length by valley bottom


# Consider applying styles

