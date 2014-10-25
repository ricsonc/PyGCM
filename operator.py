from Tkinter import *
#import traceback
#inputs are grid, timestep, and output
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import * #for step
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from PIL import Image #before just import Image
import numpy as np
import Tkinter
from threading import Thread
import md5
#REWRITE AS TKINTER


print 'INITIALIZING'
execfile("pygcmi.py")

#input
grid = cPickle.load(open('hgrid', 'rb'))
time_ = 0.2
celldata = True

#need to establish N
N = len(grid[0])
V = 4
#

def cycle(time_,grid,file):
    print 'cycle'
    print 'execfile'
    execfile(file)
    print 'timestexp'
    timestep(time_,grid)

def task(time_,grid,t):
    print 'task'
    if go and (not(t) or not(t.isAlive())): #make sure previous finished!
        #print go
        try:
            t = Thread(None,cycle,None,(time_,grid,'step.py'))
            t.start()
        except:
            print 'error'
            #traceback.print_exc()
    else:
        pass
    #print 'paused'
    g.runinput() #processes commands #yes this does exist...
    g.updatescreen()
    root.after(2000,task,time_,grid,t) 

go = True
def start():
    global go
    go = True
    #print 'started', go
def stop():
    global go
    go = False
    #print 'stopped', go
        
class GCM(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background = "white")
        self.parent = parent
        self.initUI()
        self.contents = None
    def initUI(self):
        self.parent.title("pyGCM")
        self.pack(fill=BOTH, expand = 1)
        self.centerWindow()
        self.items = {}
        #command line:
        self.xtext = Text(self,bg='grey',height=3,width=30)
        self.xtext.grid(column =1, row = 0, columnspan = 2,rowspan = 5)
        self.items['inputtext'] = self.xtext
        #print output
        self.wlabel = Label(self,text="",justify = LEFT)
        self.wlabel.grid(column= 1, row = 5, columnspan = 2, rowspan = 10)
        self.items['label'] = self.wlabel
        #buttons start and stop
        self.startb = Button(self, text = 'start', command= start)
        self.stopb = Button(self, text = 'stop', command = stop)
        self.startb.grid(column = 0,row = 0)
        self.stopb.grid(column=0,row=1)
        #optionmenu
        self.viewmode = StringVar(self)#try root if this fails
        self.viewmode.set("none")
        self.parameterlist = ("heatinput","heatoutput","circulation","coriolis2","coriolis1","temp","humidity","content","weather","achange","tchange",
                              "humidlimit","humidreduce","stormheat", "rain", "dweather", "albedo", "planthumid", "plantabsorb", "plantgrowth", "evapwater",
                              "evapsalt", "addice", "meltice", "addcontent", "salinity", "vegetation")
        self.pick = OptionMenu(self, self.viewmode, "none", *(self.parameterlist))
        self.pick.grid(column = 3, row = 6) #correct gridding?
        #to get, do self.viewmode.get()
        #second optionmenu
        self.level = StringVar(self)
        self.level.set("-1")
        self.pickl = OptionMenu(self,self.level,"-1","0","1","2","3")
        self.pickl.grid(column=4,row=6)
        #DISPLAY
        self.display = Figure(figsize=(4,8),dpi = 50)
        self.a = self.display.add_subplot(111)
        #now plot
        d = self.viewmode.get()
        lev = int(self.level.get())
        try:
            data = np.array([[col[y][lev].data[d] for y in xrange(0,N)] for col in [grid[x] for x in xrange(0,2*N)]])
        except:
            data = np.array([[random.random()*100 for x in range(N)] for y in range(2*N)])
        self.b = self.a.imshow(data) #warning, this is missing a comma! #figure out data
        self.cnv = FigureCanvasTkAgg(self.display,master=self)
        #print 'before'
        print 'b0'
        self.cnv.get_tk_widget().grid(column = 3, row = 7, columnspan = 8,rowspan=3) #causes error #CAUSES FREEZE
        #self.display.grid(column = 3, row = 6, columnspan = 5,rowspan=5)
        print 'b1'
        self.cnv.show() #stuck here?
        #self.get_tk_widget().pack(side=Tk.TOP, fill = Tk.BOTH, expand = 1)
        print 'b2'
        self.pack()
        #error here
        print 'a2'
    def centerWindow(self):
        print 'c1'
        w = 900
        h = 600
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))
    def tprint(self,str):
        m = self.items['label'].cget("text")
        m = m[m.find('\n')+1:]+'\n'+str
        self.items['label']['text'] = m
    def runinput(self): #put into loop
        print 'running'
        #print self.viewmode.get()
        m = self.items['inputtext'].get("0.0",'end')
        print 'm', m
        if len(m) > 5 and m[:4] == '#~~~' and md5.md5(m).digest() != self.contents: #becomes equal after execution, #this can be done more elegantly with a box
            print 'working'
            try: 
                exec(m in globals(), locals()) #allow looping and breaking for this later. #remove parentheses if problem
                print 'exec'
                self.contents = md5.md5(m).digest()
            except:
                print 'input error'
    def updatescreen(self):
        print 'us'
        d = self.viewmode.get()
        lev = int(self.level.get())
        #row = [grid[y] for y in xrange(0,N)]
        kb = False
        '''if d == 'heatinput':
            print '####'
            print grid[0][0][1].data['heatinput'], 'hi'
            print grid[0][0][1].data.get('heatinput'), 'heat'
            print '####'
        '''
        #try:
        #
        try:
            c=0
            data = np.array([[col[y][lev].data.get(d) for y in xrange(0,N)] for col in [grid[x] for x in xrange(0,2*N)]]) #out of range, did we swap
            for d1 in xrange(0,len(data)): #level zero has many problems!
                for d2 in xrange(0,len(data[d1])):
                    if data[d1][d2] == None:
                        data[d1][d2] = np.nan
                    else:
                        c+=1
            if c >5:
                kb = True
                        #kb = True
            
        except:
            pass
            #if d != 'none':
            #    data = [[col[y][lev].data[d] for y in xrange(0,N)] for col in [grid[x] for x in xrange(0,2*N)]]
                
        if kb:
            #print list(data)
            #data = [[c.d for c in xrange(0,2*N)] for grid[y] in xrange(0,N)] #what if none #implicate the grid?
            self.b.set_data(data) #clear this up #what is data?
            #update axes
            #self.a.relim()
            #self.a.autoscale_view(True,True,True)
            #
            min1 = min((min(lin) for lin in data))
            max1 = max((max(lin) for lin in data))
            self.b.set_clim(min1,max1)
            self.cnv.draw()
            #now loop with after
            #run this as a thread?
        else:
            print 'draw failed'
                
root = Tk() #not a problem? if it is, remove the tkinter part
root.after(2000,task,time_,grid,None)
g = GCM(root)
print 'afterroot'
root.mainloop()
print 'aftermain'
