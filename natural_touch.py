from numpy import deg2rad, sin,cos, array
from gcody import gcode, gsettings
import numpy as np
np.set_printoptions(suppress=True) # don't use scientific notation

AMOUNT_COORDS = 1000
GCODE_LINES = AMOUNT_COORDS*2
X_LIM, Y_LIM, Z_LIM = 20, 110, 85
TOUCH = 20

def get_coordinates():
  c = np.zeros(shape = (AMOUNT_COORDS,3), dtype = float)
  for i in range(0,AMOUNT_COORDS):
    c[i,0] = TOUCH
    c[i,1] = round(np.random.uniform(0,Y_LIM), 3)
    c[i,2] = round(np.random.uniform(0,Z_LIM), 3)


  #sort by z-axis
  c = c[c[:, 2].argsort()]


  gc = np.zeros(shape = (GCODE_LINES+1,3), dtype = float)
  for i in range(0,GCODE_LINES,2):
    gc[i + 1] = c[int(i/2)]

    if i > 0:
      #interim = np.add(gc[i-1], gc[i+1])/2
      interim = gc[i+1]
      gc[i] = (0, interim[1], interim[2])

  gc[GCODE_LINES] = (0, Y_LIM, Z_LIM)
  return gc

c = get_coordinates()


gset = gsettings(graphics='myplotlib')
g = gcode(settings = gset)
g.move(0,0,0, speed = 100)
g.move(X_LIM,0,0)
g.dwell(milisec=5000)

g.move(X_LIM, Y_LIM, 0)
g.move(X_LIM, Y_LIM, Z_LIM)x
g.move(X_LIM, 0, Z_LIM)
g.move(X_LIM,0,0)


g.dwell(milisec=1000)
g.move(0, 0, 0)



for i in range(0,GCODE_LINES+1):
  if i == 1:
    g.move(0, c[i,1], c[i,2])
  g.move(c[i,0], c[i,1], c[i,2])
  if i % 2:
      g.dwell(milisec=500)
      g.move(0, c[i,1], c[i,2])


g.save('ten.gcode')
g.slide_view()















