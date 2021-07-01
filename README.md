# Integrated Width

Initial script that calculates an integrated valley segment width.
 - Starts with a single geopackage containing two layers:
 - polyline named `centerline`
 - segmented polygons named `valley-bottom-segmented`

Just run the script, and it will give you two file dialogs:
 - first one asks for the input geopackage
 - second one is asking for an output directory

Final output is a geopackage containing a single segmented line layer with a `int_width_m` attribute calculated as the segment area / segment length.
