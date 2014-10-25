import numpy as np
import Image
from PIL import Image
import cPickle

execfile("settings.py")
execfile("pygcmi.py")

fname = raw_input('image name :')
scale = raw_input('scale :') #typical is 10m
i = Image.open(fname)
width, height = i.size
seaconstant= -1

N = height
V = 4

j = np.array(i)

print i.size
#100x200x3

def get3list(j):
    #stores image in format row, column, color
    ilist = []
    for x in xrange(0,width):
        row = []
        for y in xrange(0,height):
            column = []
            for z in xrange(0,3):
                #print x,y,z
                value = j[y][x][z]
                column.append(value)
            row.append(column)
        ilist.append(row)
    return ilist

#rearranges image into format row, column, height
def gethlist(ilist):
    heightmap = []
    for x in xrange(0,width):
        row = []
        for y in xrange(0,height):
            row.append(0)
        heightmap.append(row)

    for x in xrange(0,width):
        for y in xrange(0,height):
            t = ilist[x][y]
            if t[1] != t[2]:
                heightmap[x][y]= seaconstant
            else:
                heightmap[x][y] = t[0]*scale

    return heightmap

grid = [] #dimensions are n by 2n by v
for x in xrange(0,2*N):
	t1 = []
	for y in xrange(0,N):
		t2 = []
		for z in xrange(0,V):
			t2.append(0)
		t1.append(t2)
	grid.append(t1)

def altinput(alt,grid,N):
	for x in xrange(0,2*N):
		for y in xrange(0,N):
			if alt[x][y] != -1: #zone is land
				grid[x][y][0] = None
				grid[x][y][1] = LAND(1,x,y,TEMPGRAD(y),VEGALB(random.random()),alt[x][y],VEGWAT(random.random()), 0.0, random.random())
			elif alt[x][y] == -1.0: #zone is sea
				for z in xrange(0,2):
					if z == 0:
						d = True
					else:
						d = False
					grid[x][y][z] = SEA(z,x,y,TEMPGRAD(y),SEAALB,INITSEADIR(),SALINITY(),INITVEG(),d,0.0)

			for z in xrange(2,V): #add the air
				grid[x][y][z] = AIR(z,x,y,TEMPGRAD(y),AIRALB,INITAIRDIR(),INITHUMID(), INITWEATHER(),INITCONTENT, INITPRESSURE())
	return grid

m = altinput(gethlist(get3list(j)),grid,N)

cPickle.dump(m, open('hgrid', 'wb'))
#
