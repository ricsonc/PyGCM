#CONSTANTS AND FUNCTIONS

def latcir(int):
	x = (y+0.5)/N
	x = 2*abs(x-0.5)
	c = (1-x**2)**0.5
	return c

#IMPORTANT VARIABLES
ABSTIME = 0.0

def INTENSITY(l, j, y): #NOT USED but should be #it is used. but what is x? #replaced all x with l, seems to be working.
	global ABSTIME
	l = (l+0.5)/N
	l = 2*abs(l)
	l *= math.pi/180.0
	t = t = j*math.sin(2.0*math.pi*l/y)
	n = math.cos(math.pi-l-t)
	m = math.cos(l-t)
	a = 0.5*(m-n)
	flux = a*math.sin(2*math.pi*l)+(m-a)
	return flux #range(0,1)

def ALTTEMP(cell,time): #this is not used...?
	return cell.temp-ALTCONSTANT*cell.v

def TEMPPRESSURE(temp,constant):
	pressure = (temp+273)/constant
	return pressure

def SALPRESSURE(temp,constant,salinity,sconstant):
	pressure = ((temp+273)/constant)-salinity*sconstant
	return pressure

#CONDITION CONSTANTS
INDUSTRY = 0.0
FLUX = 1.0
AIRALB = 0.3
SEAALB = 0.2
TIMELEN = 1.0
REVTIME = 100

BOLTZMANN = 4 ##power to which temperature is dispersed when temperature rises

AIRHEAT= 1.0
SEAHEAT= 1.0
LANDHEAT= 1.0

AIRRAD = 1.0
SEARAD = 0.2
LANDRAD = 0.2

GRAVITY = 1.0
AIRPRESSURECONSTANT = 1.0
SEAPRESSURECONSTANT = 2.0

AIRTPCONSTANT = 100.0
SEATPCONSTANT = 200.0

CORIOLISCONSTANT = 2.0

AIRPRESSUREDELAY = 0.5
SEAPRESSUREDELAY = 0.9

AIRPARAMS = ["temp","humidity","content","weather"]
SEAPARAMS = ["temp","salinity","vegetation"]

AIRWEIGHTS = [1.0,0.7,0.5,0.5]
SEAWEIGHTS = [1.0,2.0,0.1]

SALCONSTANT = 1.0

STORMLIMIT = 10.0
HUMIDLIMIT = 10.0

STORMHEAT = 0.9
STORMREDUCE = 20

EVAPRATE = 1.0
EVAPSAL = 1.0

PLANTCONTENT = 1.0
PLANTALBEDO = 1.0
PLANTHUMID = 1.0

BACKGROUNDCONTENT = 0.6

OCEANALBEDO = 0.1
ICEALBEDO = 0.4
ICETEMP = 0.0

STORMWET = 1.0

SEAPLANTMINTEMP = 25.0
SEAPLANTMAXTEMP = 20.0
MAXSEAVEGETATION = 2.0

ALTCONSTANT = 1/200.0

LANDCAPACITY = 0.2
SEACAPACITY = 2
AIRCAPACITY = 0.1

AIRSEAEXCHANGE = 2.0
AIRLANDEXCHANGE = 1.0

PLANTWETNESS = 1.0

AXIALTILT = 0.41   #in radians
YEARLENGTH = 365

LANDMELTRATE = 1.0
SEAMELTRATE = 3.0

STORMCONDITION = 50.0
SEEDSIZE = 1.0

LANDFREEZERATE = 1.0
SEAFREEZERATE = 1.0
MAXSEAICE = 100.0

STORMHUMID = 5.0

MINFLOAT = 1e-100

#THESE CONSTANTS ARE FOR USE IN RENDERING

DIRMIN = -1000
DIRMAX = 1000

#################################################

#ALTINPUT
def TEMPGRAD(lat): #temperature at latitude
	temp = random.random()*35-10
	return temp

def VEGALB(veg): #albedo caused by land vegetation
	alb = random.random()*veg
	return alb

def VEGWAT(veg): #water needed by plant amount
	wat = random.random()*veg
	return wat

#constants
INITCONTENT = 0.3

def INITSEADIR():
	dir = [random.random(),random.random(),random.random()]
	return dir

def INITAIRDIR():
	dir = [random.random(),random.random(),random.random()]
	return dir

def SALINITY():
	sal = random.random()
	return sal

def INITVEG():
	veg = random.random()
	return veg

def INITWEATHER():
	weather = random.random()
	return weather

def INITPRESSURE():
	pressure = [random.random(),random.random(),random.random()]
	return pressure

def INITHUMID():
	return random.random()



#END CONSTANTS
