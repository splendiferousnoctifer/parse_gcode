import gcody as g

# a file to read 
file = '/Volumes/GoogleDrive-104257292494891488592/My Drive/mil/natural_touch/parse_gcode/demo/elefante_small.gcode'

# setting graphics backend to be mayavi
settings = g.gsettings(graphics='matplotlib')


# reading gcode file
elefante = g.read(file, settings=settings)


# standard viewing of gcode
elefante.view(elefante.t,colormap='jet', figsize=(1500,1500))


# viewing the gcode
elefante.cbar_view(figsize=(1500,1500))







