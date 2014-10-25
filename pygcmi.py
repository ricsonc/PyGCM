import math
import cPickle
import time
import random
import copy
#import pickle

#x is east/west, y is north/south, z is up, down

execfile('settings.py')

class CELL:
	def __init__(self,v,x,y,temp,albedo,type):
		self.area = latcir(y)
		self.temp = temp
		self.albedo = albedo
		self.type = type
		self.v = v
		self.x = x
		self.y = y
		self.data = {}

class AIR(CELL):
	def __init__(self,v,x,y,temp,albedo,direction,humidity,weather,content,pressure):
		CELL.__init__(self,v,x,y,temp,albedo,'air')
		self.direction = direction
		self.humidity = humidity
		self.weather = weather
		self.content = content
		self.pressure = pressure
class LAND(CELL):
	def __init__(self,v,x,y,temp,albedo,height,wetness,ice, vegetation):
		CELL.__init__(self,v,x,y,temp,albedo,'land')
		self.wetness = wetness
		self.height = height
		self.ice = ice
		self.vegetation = vegetation

class SEA(CELL):
	def __init__(self,v,x,y,temp,albedo,direction,salinity,vegetation,deep,ice):
		CELL.__init__(self,v,x,y,temp,albedo,'sea')
		self.direction = direction
		self.salinity = salinity
		self.vegetation = vegetation
		self.deep = deep
		self.ice = ice

#input alt data into the grid

#######
#INPUT AND OUTPUT
######

#NORM DATA INPUT
def input(grid):
	grid = cPickle.load(open('grid', 'rb'))

#NORM DATA OUTPUT
def output(grid):
	cPickle.dump(grid, open('grid', 'wb'))

##########
#SIMULATE
#########

def griditerate(function,time,grid, ggrid):
	for x in xrange(0,2*N):
		for y in xrange(0,N):
			for z in xrange(0,V):
				if ggrid[x][y][z] and ggrid[x][y][z] != 0: #wth does this do. tell me now! #check for null cells? overcomplicated?
					function(ggrid[x][y][z],time,grid) #ggrid, because of direct modifications
	#griditerate passes cell to functions
	#ggrid is the clone, grid is the real one
	#the one passed should be the real one, the one given for viewing should be the clone
					
def heatinput(cell,time,grid): #adjusted for area not necessary 
	if cell.type == 'air':
		tempinc = (1-cell.albedo)*FLUX*time*AIRHEAT*(1+cell.content)*INTENSITY(cell.y, AXIALTILT, YEARLENGTH) #wrong place to put altitude *1/cell.v
	elif cell.type == 'sea' and not(cell.deep):
		if cell.ice == False:
			tempinc = (1-cell.albedo)*FLUX*time*SEAHEAT*INTENSITY(cell.y, AXIALTILT, YEARLENGTH)
		else:
			tempinc = (1-ICEALBEDO)*FLUX*time*SEAHEAT*INTENSITY(cell.y, AXIALTILT, YEARLENGTH)
	elif cell.type == 'sea' and cell.deep:
		tempinc = 0
	elif cell.type == 'land':
		if cell.ice == 0:
			tempinc = (1-cell.albedo)*FLUX*time*LANDHEAT*INTENSITY(cell.y, AXIALTILT, YEARLENGTH)
		else:
			tempinc = (1-ICEALBEDO)*FLUX*time*LANDHEAT*INTENSITY(cell.y, AXIALTILT, YEARLENGTH)
	else:
		print 'error 268'
		#there is a big problem
	cell.temp += tempinc
	celladd(cell,'heatinput',tempinc)
	#cell.data['heatinput'] = tempinc #should this be given a conditional?

def heatoutput(cell,time,grid): #upper atmosphere radiates most
	if cell.type == 'air':
		tempdec = 1/(time*(cell.temp+273)**BOLTZMANN)*AIRRAD*ALTTEMP(cell,time)
	elif cell.type == 'sea' and not(cell.deep):
		tempdec = 1/(time*(cell.temp+273)**BOLTZMANN)*SEARAD
	elif cell.type == 'sea' and cell.deep:
		tempdec = 0
	elif cell.type == 'land':
		tempdec = 1/(time*(cell.temp+273)**BOLTZMANN)*LANDRAD
	else:
		print 'error 282'
	cell.temp -= tempdec
	celladd(cell,'heatoutput',tempdec)
	#cell.data['heatoutput'] = tempdec
		#there is a big problem
	#return cell

#START CIRCULATION FUNCTION
def circulation_pressure(cell,time,grid,top,bottom):
	#remove pressure for the other cell and incorporate time!!!
	#different variables for sea and land* done
	#what are top and bottom.. should be replaced by grid
	if bottom == 0:
		#sea constants
		tpc = SEATPCONSTANT
		spc = SALCONSTANT
		pressureconstant = SEAPRESSURECONSTANT
		t2 = SALPRESSURE(cell.temp,tpc,cell.salinity,spc)-GRAVITY

	else:
		tpc = AIRTPCONSTANT
		pressureconstant = AIRPRESSURECONSTANT
		t2 = TEMPPRESSURE(cell.temp,tpc)-GRAVITY

		#air constants

	#this block subtracts pressure from top/bottom
	if cell.v == top and grid[cell.x][cell.y][cell.v-1] : 
		t2 += time*pressureconstant*grid[cell.x][cell.y][cell.v-1].direction[2] #get pressure of cell below and add it to t2
		ct2 = grid[cell.x][cell.y][cell.v-1].direction[2] 						#get direction of that cell 
		ct2 -= t2																#subtract the pressure from direction
		grid[cell.x][cell.y][cell.v-1].direction[2] = ct2						#assign that direction back to the cell
	elif cell.v == bottom and grid[cell.x][cell.y][cell.v+1] :
		t2 += time*-1*pressureconstant*grid[cell.x][cell.y][cell.v+1].direction[2] 	#get negative pressure of cell above
		ct2 = grid[cell.x][cell.y][cell.v+1].direction[2]							#get direction of cell
		ct2 -= t2																	#add pressure to direction
		grid[cell.x][cell.y][cell.v+1].direction[2] = ct2							#assign that direction back to the cell
	elif bottom < cell.v < top and grid[cell.x][cell.y][cell.v-1] and grid[cell.x][cell.y][cell.v+1] :
		t21 = time*pressureconstant*grid[cell.x][cell.y][cell.v-1].direction[2] #same thing, but for middle cell, and air gets moved both ways
		ct2 = grid[cell.x][cell.y][cell.v-1].direction[2]
		ct2 -= t21
		grid[cell.x][cell.y][cell.v-1].direction[2] = ct2
		t22 = time*-1*pressureconstant*grid[cell.x][cell.y][cell.v+1].direction[2]
		ct2 = grid[cell.x][cell.y][cell.v+1].direction[2]
		ct2 -= t22
		grid[cell.x][cell.y][cell.v+1].direction[2] = ct2
		t2 += t21+t22
	else:
		print 'error 326'
		
	#this block deals with pressures from horizontally adjacent cells
	t1 = 0
	if cell.y < N-1 and grid[cell.x][cell.y+1][cell.v] and grid[cell.x][cell.y+1][cell.v].type != 'land': 
		t1 += time*pressureconstant*grid[cell.x][cell.y+1][cell.v].direction[1] #get pressure of adjacent cell
		ct1 = grid[cell.x][cell.y+1][cell.v].direction[1]						#get direction of adjacent cell
		ct1 -= t1																#subtract pressure from direction
		grid[cell.x][cell.y+1][cell.v].direction[1] = ct1						#assign direction bcak to cell
	if cell.y > 0 and grid[cell.x][cell.y-1][cell.v] and grid[cell.x][cell.y-1][cell.v].type != 'land':
		t1 += time*pressureconstant*grid[cell.x][cell.y-1][cell.v].direction[1]
		ct1 = grid[cell.x][cell.y-1][cell.v].direction[1]
		ct1 -= t1
		grid[cell.x][cell.y-1][cell.v].direction[1] = ct1
	t0 = 0
	if (cell.x+1 % N) < 2*N-1 and grid[cell.x+1][cell.y][cell.v] and grid[cell.x+1][cell.y][cell.v].type != 'land':
		t0 += time*pressureconstant*grid[cell.x+1][cell.y][cell.v].direction[0]
		ct0 = grid[cell.x+1][cell.y][cell.v].direction[0]
		ct0 -= t0
		grid[cell.x+1][cell.y][cell.v].direction[0] = ct0
	if cell.x > -1 and grid[cell.x-1][cell.y][cell.v] and grid[cell.x-1][cell.y][cell.v].type != 'land':
		t0 += time*pressureconstant*grid[cell.x-1][cell.y][cell.v].direction[0]
		ct0 = grid[cell.x-1][cell.y][cell.v].direction[0]
		ct0 -= t0
		grid[cell.x-1][cell.y][cell.v].direction[0] = ct0

	#this adds it onto the current cell.
	cell.pressure =  [t0,t1,t2] #the amount that was subtracted from other cells..gets moved to the current cell!
	celladd(cell,'circulation',cell.pressure)
	#cell.data['circulation'] = cell.pressure

def circulation_direction(cell,time,pressuredelay):
	#compute direction with pressure
	cell.direction = []
	for item in cell.pressure:
		cell.direction.append(item*pressuredelay)
	cell.data['directon'] = cell.direction	

def circulation_coriolis(cell,time):
	#adjust for coriolis
	#acceleratoin = -2 angular velocity * velocity *sin (angle)
	angle = math.atan(cell.direction[1]/(cell.direction[2]+MINFLOAT)) #div by zero
	coriolis = -cell.area*cell.direction[2]*math.sin(angle)*CORIOLISCONSTANT
	cell.direction[2] += coriolis
	#cell.data['coriolis2'] = coriolis
	celladd(cell,'coriolis2',coriolis)
	if cell.direction[1] > coriolis:
		coriolis *= -1
	elif cell.direction[1] < coriolis:
		#coriolis *= 1
		pass
	else:
		coriolis = random.random()-0.5
	cell.direction[1] += coriolis
	celladd(cell,'coriolis1',coriolis)
	#cell.data['coriolis1'] = coriolis
	#taxicab coordinate system used, no pythagorean to save time.

def circulation_move(cell,time):
	#move air, pressuredelay here would be redundant
	for x in xrange(0,3):
		cell.pressure[x] -= cell.direction[x]
	#no need for cell.data here

def circulation_params(cell,time,grid,top,bottom,attrs,weights): #subtracts and adds
	#move content, weather, humidity

	for x in xrange(0,len(attrs)):
		attr = attrs[x]
		weight = weights[x]
		val = getattr(cell, attr)		
		dval = 0.0 #deltaval
		ival = 0.0
		if cell.v == top:
			if cell.direction[2] > 0:
				cval = getattr(grid[cell.x][cell.y][cell.v-1],attr)
				ival = time*weight*cell.direction[2]*cval*cell.area #add to cell
				cval -= ival
				setattr(grid[cell.x][cell.y][cell.v-1],attr,cval)
		elif cell.v == bottom:
			if cell.direction[2] < 0:
				cval = getattr(grid[cell.x][cell.y][cell.v+1],attr)
				ival = time*weight*cell.direction[2]*cval*cell.area
				cval -= ival
				setattr(grid[cell.x][cell.y][cell.v+1],attr,cval)
		elif cell.v < top:
			cval = getattr(grid[cell.x][cell.y][cell.v+1],attr)
			val21 = time*weight*cell.direction[2]*cval*cell.area
			cval -= val21
			setattr(grid[cell.x][cell.y][cell.v+1],attr,cval)
			cval = getattr(grid[cell.x][cell.y][cell.v-1],attr)
			val22 = time*weight*cell.direction[2]*cval*cell.area
			cval -= val22
			setattr(grid[cell.x][cell.y][cell.v-1],attr,cval)
			ival = val21+val22
		else:
			print 'error 415'
		dval += ival
		ival = 0.0
		if cell.y < N-1 and grid[cell.x][cell.y+1][cell.v] and grid[cell.x][cell.y+1][cell.v].type != 'land':
			cval = getattr(grid[cell.x][cell.y+1][cell.v],attr)
			ival = time*weight*cell.direction[1]*cval*cell.area
			cval -= ival
			setattr(grid[cell.x][cell.y+1][cell.v],attr,cval)
		if cell.y > 0 and grid[cell.x][cell.y-1][cell.v] and grid[cell.x][cell.y-1][cell.v].type != 'land':
			cval = getattr(grid[cell.x][cell.y-1][cell.v],attr)
			ival = time*weight*cell.direction[1]*cval*cell.area
			cval -= ival
			setattr(grid[cell.x][cell.y-1][cell.v],attr,cval)
		dval+= ival
		ival = 0.0
		if (cell.x+1 % N) < 2*N-1 and grid[cell.x+1][cell.y][cell.v] and grid[cell.x+1][cell.y][cell.v].type != 'land': #index error here for some reason!
			cval = getattr(grid[cell.x+1][cell.y][cell.v],attr)
			ival = time*weight*cell.direction[0]*cval*cell.area
			cval -= ival
			setattr(grid[cell.x][cell.y][cell.v],attr,cval)
		if cell.x > -1 and grid[cell.x-1][cell.y][cell.v] and grid[cell.x-1][cell.y][cell.v].type != 'land':
			cval = getattr(grid[cell.x-1][cell.y][cell.v],attr)
			ival = time*weight*cell.direction[0]*cval*cell.area
			cval -= ival
			setattr(grid[cell.x-1][cell.y][cell.v],attr,cval)
		dval += ival

		val += dval
		setattr(cell,attr,val) #this is not right, val gets reset every time.
		celladd(cell,attr,val)
		#cell.data[attr] = val

#END ATMOSCIR FUNCTIONS

def circulation(cell,time,grid,top,bottom,params,weights): #intercell transfer
	circulation_pressure(cell,time,grid,top,bottom)
	if bottom == 0:
		circulation_direction(cell,time,AIRPRESSUREDELAY)
	else:
		circulation_direction(cell,time,SEAPRESSUREDELAY)

	circulation_coriolis(cell,time)
	circulation_move(cell,time)
	circulation_params(cell,time,grid,top,bottom,params,weights)

def atmoscir(cell,time,grid): #must return something
	if cell.type == 'air':
		circulation(cell,time,grid,V-1,2,AIRPARAMS,AIRWEIGHTS)
		
def oceancir(cell,time,grid): #must return something
	if cell.type == 'sea':
		circulation(cell,time,grid,1,0,SEAPARAMS,SEAWEIGHTS)

def verticaltransfer(cell,time,grid): #pass air cells to this
	if cell.type == 'air' and cell.v == 2:
		diff = cell.temp - grid[cell.x][cell.y][cell.v-1].temp #difference in temperature between two cells
		if grid[cell.x][cell.y][cell.v-1] and grid[cell.x][cell.y][cell.v-1].type == 'sea':
			change = diff*time*AIRSEAEXCHANGE
			achange = change/AIRCAPACITY
			tchange = change/SEACAPACITY
		elif grid[cell.x][cell.y][cell.v-1] and grid[cell.x][cell.y][cell.v-1].type == 'land':
			change = diff*time*AIRLANDEXCHANGE
			achange = change/AIRCAPACITY
			tchange = change/LANDCAPACITY
		else:
			print 'error 485'
		cell.temp -= achange
		grid[cell.x][cell.y][cell.v-1].temp += tchange
		celladd(cell,'achange',achange)
		celladd(cell,'tchange',tchange)
		#cell.data['achange'] = achange #APPLIES TO AIR CELLS
		#cell.data['tchange'] = tchange #LAND AND SEA CELLS
##WEATHER FUNCTION

def humidlimit(cell,time):
	#cell.data['humidlimit'] = False
	celladd(cell,'humidlimit',False)
	if cell.humidity/(cell.temp+273) > HUMIDLIMIT: #replace 273 with another constant? maybe.
		cell.humidity = HUMIDLIMIT*(cell.temp+273)
		celladd(cell,'humidlimit',True)
		#cell.data['humidlimit'] = True

def humiditylower(cell,time): #for air cells only
	humidreduce = cell.humidity/STORMREDUCE*cell.weather*time
	cell.humidity -= humidreduce
	celladd(cell,'humidreduce',humidreduce)
	#cell.data['humidreduce'] = humidreduce

def heatmove(cell,time,grid):
	heatchange = STORMHEAT*cell.weather*time
	cell.temp -= heatchange
	celladd(cell,'stormheat',heatchange)
	#cell.data['stormheat'] = heatchange #add to above? no?
	grid[cell.x][cell.y][cell.v+1].temp += heatchange

def wetraise(cell,time,grid):
	if grid[cell.x][cell.y][cell.v-1] and grid[cell.x][cell.y][cell.v-1].type == 'land':
		addwet = STORMWET*cell.weather*time
		celladd(cell,'rain',addwet)
		#cell.data['rain'] = addwet
		grid[cell.x][cell.y][cell.v-1].wetness += addwet
		#add to sky?
	#sea ice formation dependent on percipitation or flow.

def stormdelta(cell,time):
	cell.data['dweather'] = 0
	if cell.v <= (V-2)/2+1 and random.uniform(cell.humidity/2,cell.humidity)/(cell.temp+273) > STORMLIMIT: #should altitude be used here???
		cell.weather += SEEDSIZE #
		celladd(cell,'dweather',SEEDSIZE)
		#cell.data['dweather'] = SEEDSIZE
	#conditions that increase: humidity, convection
	if cell.weather > 0:
		dweather = (cell.humidity-STORMHUMID)/(cell.temp+273)*STORMCONDITION*time #low temp lowers vapor pressure
		celladd(cell,'dweather',dweather)
		#cell.data['dweather'] = dweather
		cell.weather += dweather
				
def stormeffect(cell,time,grid): #all 3 function need to be affected by cell.weather. #done
	humiditylower(cell,time)
	heatmove(cell,time,grid)
	wetraise(cell,time,grid) #doesn't apply to cell.type == 'water'
		
def storm(cell,time,grid):
	if cell.type == 'air' and cell.v < V-1:
		stormdelta(cell,time)
		stormeffect(cell,time,grid)	

#END WEATHER FUNCTIONS

def weather(cell,time,grid):
	if cell.type == 'air':
		humidlimit(cell,time)
	storm(cell,time,grid) #in storm, the if-air condition is tested inside function

#VEGETATION FUNCTION
def albedocompute(cell,time):
	cell.albedo = 0.7-cell.vegetation*PLANTALBEDO
	celladd(cell,'albedo',cell.albedo)
	#cell.data['albedo'] = cell.albedo
	if cell.albedo < 0:
		cell.albedo = 0

def humidityincrease(cell,time,grid):
	planthumid = PLANTHUMID*cell.vegetation*time
	grid[cell.x][cell.y][cell.v+1].humidity += planthumid
	celladd(cell,'planthumid',planthumid)
	#cell.data['planthumid'] = planthumid
	#no limit to cell humidity yet

def contentdecrease(cell,time,grid): 
	if cell.type == 'land' or (cell.type == 'sea' and cell.v == 1):
		plantabsorb = PLANTCONTENT*cell.vegetation*time
		grid[cell.x][cell.y][cell.v+1].content -= plantabsorb
		celladd(cell,'plantabsorb',plantabsorb)
		#cell.data['plantabsorb'] = plantabsorb
		if grid[cell.x][cell.y][cell.v+1].content < 0:
			grid[cell.x][cell.y][cell.v+1].content = 0

def plantgrowth(cell,time):
	if cell.type == 'land':
		if cell.wetness < PLANTWETNESS*cell.vegetation:
			change = 0.9**time
		else:
			change = 1.05**time
	elif cell.type == 'sea':
		if cell.temp < SEAPLANTMAXTEMP and cell.temp > SEAPLANTMINTEMP:
			change = 0.9**time
		else:
			if cell.vegetation > MAXSEAVEGETATION:
				change = 1
			else:
				change = 1.05**time
	else:
		print error
	cell.vegetation *= change
	celladd(cell,'growth',change)
	#cell.data['growth'] = change

#END VEG FUNCTION

def vegetation(cell,time,grid):
	if cell.type == 'land':
		albedocompute(cell,time)
		humidityincrease(cell,time,grid)
	if cell.type != 'air':
		contentdecrease(cell,time,grid)
		plantgrowth(cell,time)

def evaporation(cell,time,grid):
	if cell.type == 'sea' and not cell.deep:
		evapwater = grid[cell.x][cell.y][cell.v+1].temp*EVAPRATE*time
		grid[cell.x][cell.y][cell.v+1].humidity += evapwater
		evapsalt = grid[cell.x][cell.y][cell.v+1].temp*EVAPRATE*EVAPSAL*time
		cell.salinity += evapsalt
		celladd(cell,'evapwater',evapwater)
		celladd(cell,'evapsalt',evapsalt)
		#cell.data['evapwater'] = evapwater
		#cell.data['evapsalt'] = evapsalt #should we bother storing this in the below layer? no.

def ice(cell,time,grid): #are theere conditions that check for sea cell?
	if (cell.type == 'sea' or cell.type == 'land') and cell.v > 0: #FREEZING
		addice = 0
		if cell.temp < ICETEMP: #add percipitation dependence #edit, wetness dependence
			if cell.type == 'land':
				addice = cell.wetness*LANDFREEZERATE*time
			elif cell.type == 'sea':
				addice = -(cell.temp+273)*SEAFREEZERATE*time
				if addice > MAXSEAICE:
					addice = MAXSEAICE
			else:
				print 'big problem'
		cell.ice += addice
		celladd(cell,'addice',addice)
		#cell.data['addice'] = addice
		meltice = 0
		if cell.temp > ICETEMP and cell.ice: #MELTING #replace with ice flag? #done
			if cell.type == 'land':
				meltice = cell.temp*LANDMELTRATE*time
			if cell.type == 'sea':
				meltice = cell.temp*SEAMELTRATE*time
			if cell.ice - meltice < 0: #this could be done more efficiently if it wasn't for cell.data
				meltice = cell.ice
			cell.ice -= meltice
		celladd(cell,'meltice',meltice)
		#cell.data['meltice'] = meltice
	
def content(cell,time,grid):
	if cell.type == 'air':
		addcontent = BACKGROUNDCONTENT*time
		cell.content += addcontent
		celladd(cell,'addcontent',addcontent)
		#cell.data['addcontent'] = addcontent

def celladd(cell,key,value):
	if celldata: #ha
		cell.data[key] = value #THIS DOESN'T WORK! #ah-ha...are we adding to the wrong grid?
		#print 'added'
	else:
		pass

def null(cell,time,grid): #for timing purposes
	pass

def clone(grid):
	return cPickle.loads(cPickle.dumps(grid, -1))

order = [heatinput, heatoutput, atmoscir, oceancir, verticaltransfer, weather, vegetation, evaporation, ice, content, null]

def timestep(time_, grid):
	start = time.time()
	global ABSTIME
	clonegrid = clone(grid)
	#print ggrid
	print time.time()-start, clone
	for func in order:
		now = time.time() #this and next next line below are for profiling only
		griditerate(func,time_,clonegrid,grid)
		print time.time()-now, str(func)
	ABSTIME += time_
