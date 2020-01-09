posV = []
with open('seeds/S001_11.txt') as f:
	for l in f.readlines():
		line = l.rstrip()
		if line:
			posV.append(tuple(map(int,l.split(' '))))
x0 = min(x for x,_,_ in posV)
x1 = max(x for x,_,_ in posV)
y0 = min(y for _,y,_ in posV)
y1 = max(y for _,y,_ in posV)
z0 = min(z for _,_,z in posV)
z1 = max(z for _,_,z in posV)

import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as pgl
vertV = np.array([
	[ .5,-.5,-.5],
	[-.5,-.5,-.5],
	[-.5, .5,-.5],
	[-.5,-.5, .5],
	[ .5, .5,-.5],
	[ .5, .5, .5],
	[-.5, .5, .5],
	[ .5,-.5, .5] 
])
vertF = np.array([
	[1,0,7], [1,3,7],
	[1,2,4], [1,0,4],
	[1,2,6], [1,3,6],
	[0,4,5], [0,7,5],
	[2,4,5], [2,6,5],
	[3,6,5], [3,7,5]
])
colorF = np.array([
	(.4,.4*.5,.0,1),(.4,.4*.5,.0,1),
	(.5,.5*.5,.0,1),(.5,.5*.5,.0,1),
	(.6,.6*.5,.0,1),(.6,.6*.5,.0,1),
	(.7,.7*.5,.0,1),(.7,.7*.5,.0,1),
	(.8,.8*.5,.0,1),(.8,.8*.5,.0,1),
	(.9,.9*.5,.0,1),(.9,.9*.5,.0,1)
])
def vertMarker(x,y,z):
	it = pgl.GLMeshItem(vertexes=vertV, faces=vertF, faceColors=colorF, smooth=False, computeNormals=False)
	it.translate(x,y,z)
	return it

i = 0
app = pg.mkQApp()
view = pgl.GLViewWidget()
view.showMaximized()
# view.show()

posS = set(posV)
for pos in posV:
	x,y,z = pos
	if (x-1,y,z) in posS and (x+1,y,z) in posS and (x,y-1,z) in posS and (x,y+1,z) in posS and (x,y,z-1) in posS and (x,y,z+1) in posS:
		continue
	i += 1
	view.addItem(vertMarker(*pos))

view.setBackgroundColor((.1,.1,.1))
view.pan((x0+x1)/2,(y0+y1)/2,(z0+z1)/2)
view.setCameraPosition(None,1.5*(z1-z0),45,-45)
app.exec_()