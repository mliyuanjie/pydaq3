import tkinter as tk 
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import src.displayer as dp
import time
from matplotlib import style
from multiprocessing import Process, Queue
import json
import os
from src.datadaq2 import startserver
from src.calculate_events import NanoporeAssist
from src.analysis_events import EventsAnalysis
style.use(['ggplot', 'fast'])



class DaqGui():
    def __init__(self, mainwindow: tk.Tk, que_read : Queue, que_write : Queue):
        #main window initialize
        self.root = mainwindow
        self.root.title('Nanopre Daq')
        self.root.geometry('1100x600')
        #self.root['bg'] = 'black'
        self.que_read = que_read
        self.que_write = que_write

        self.filename= tk.StringVar()
        self.filename.set('new')
        self.foldername= tk.StringVar()
        self.foldername.set(os.getcwd())
        self.frame= tk.StringVar()
        self.frame.set('0 Hz')
        self.speed= tk.StringVar()
        self.speed.set('0 ms')
        self.eventnumber= tk.IntVar()
        self.eventnumber.set('0')
        self.lp = tk.IntVar()
        self.lp.set(15)
        self.current = tk.DoubleVar()
        self.current.set(0.0)
        self.stdev = tk.DoubleVar()
        self.stdev.set(0.0)
        self.voltage = tk.DoubleVar()
        self.voltage.set(0)
        self.th = tk.IntVar()
        self.th.set(30)
        self.voltagei = tk.DoubleVar()
        self.voltagei.set(0)
        self.xwindow = tk.DoubleVar()
        self.xwindow.set(5)

        self.protocol_mode = tk.StringVar() 
        self.menu = tk.Menu(self.root)
        self.menu.add_command(label = 'Protocol', command=self.setprotocol)
        self.menu.add_command(label = 'Assistant', command=self.nanoporecalculator)
        self.menu.add_command(label = 'Analysis', command=self.showAnalysis)
        self.root.config(menu=self.menu)

        self.playbutton = tk.Button(self.root, text='Play', command=self.play)
        self.playbutton.place(x=10, y = 10, width = 70, height = 30)
        self.resetbutton = tk.Button(self.root, text='Flush', command=self.flush)
        self.resetbutton.place(x=90, y = 10, width = 70, height = 30)
        self.recordbutton = tk.Button(self.root, text = 'Record', command=self.record)
        self.recordbutton.place(x=10, y = 50, width = 70, height = 30)
        tk.Label(self.root, textvariable=self.foldername).place(x=170, y = 10, width = 320, height = 30)
        tk.Entry(self.root, textvariable=self.filename).place(x=90, y = 50, width = 400, height = 30)
        tk.Button(self.root, text = 'Select', command=self.openfolder).place(x=500, y = 10, width = 70, height = 30)
        
        #tk.Entry(self.root, textvariable=self.runtime).place(x=500, y = 70, width = 70, height = 30)
   
        
        tk.Label(self.root, text = 'x:').place(x=660, y = 10, width = 30, height = 30)
        tk.Label(self.root, text = 'y:').place(x=660, y = 50, width = 30, height = 30)
        tk.Button(self.root, text = 'Center', command=self.setxwindow).place(x=740, y = 10, width = 70, height = 30)
        tk.Entry(self.root, textvariable=self.xwindow).place(x=700, y = 10, width = 30, height = 30)
        tk.Entry(self.root, textvariable=self.th).place(x=700, y = 50, width = 30, height = 30)
        tk.Button(self.root, text = 'Center', command=self.home).place(x=740, y = 50, width = 70, height = 30)
        #tk.Label(self.root, textvariable=self.frame).place(x=820, y = 10, width = 70, height = 30)
        #tk.Label(self.root, textvariable=self.eventnumber).place(x=820, y = 50, width = 70, height = 30)
        tk.Label(self.root, textvariable=self.speed).place(x=580, y = 10, width = 70, height = 30)
     
        tk.Entry(self.root, textvariable=self.lp).place(x=500, y = 50, width = 70, height = 30)
        tk.Button(self.root, text = 'Filter', command=self.filter).place(x=580, y = 50, width = 70, height = 30)
        tk.Label(self.root, text = 'current pA:').place(x=820, y = 10, width = 80, height = 30)
        tk.Label(self.root, textvariable=self.current).place(x=900, y = 10, width = 90, height = 30)
        tk.Label(self.root, text = '±').place(x=990, y = 10, width = 60, height = 30)
        tk.Label(self.root, textvariable=self.stdev).place(x=1040, y = 10, width = 50, height = 30)
        tk.Entry(self.root, textvariable=self.voltage).place(x=820, y = 50, width = 70, height = 30)
        tk.Label(self.root, textvariable=self.voltagei).place(x=980, y = 50, width = 80, height = 30)
        tk.Label(self.root, text='mV').place(x=1060, y = 50, width = 30, height = 30)
        tk.Button(self.root, text = 'Apply', command=self.apply).place(x=900, y = 50, width = 70, height = 30)
        
        #tk.Label(self.root, text = 'lp nm:').place(x=1120, y = 10, width = 70, height = 30)
        #tk.Entry(self.root, textvariable=self.length).place(x=1190, y = 10, width = 70, height = 30)
        #tk.Label(self.root, text = 'ld nm:').place(x=1120, y = 50, width = 70, height = 30)
        #tk.Entry(self.root, textvariable=self.diameter).place(x=1190, y = 50, width = 70, height = 30)
        


        self.fig = Figure()
        self.ax = self.fig.add_subplot(1,1,1)
        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.get_tk_widget().place(x = 0, y = 90, width=1100, height = 450) 
        self.time_start = time.time()

        self.y1 = tk.Entry(self.root)
        self.y1.bind('<Return>', self.setylim)
        self.y1.insert(0, "100")
        self.y1.place(x=10, y = 100, width = 70, height = 30)

        self.y2 = tk.Entry(self.root)
        self.y2.bind('<Return>', self.setylim)
        self.y2.insert(0, "-100")
        self.y2.place(x=10, y = 500, width = 70, height = 30)

        self.display = dp.DisplayRealTime(self.ax, float(self.xwindow.get()), [-100,100])
        #f= open('./iv.json')
        self.ParameterVar = {}
        self.obj_slot = {
                        "current_plot": self.currentPlot,
                        "mean_change": self.setcurrent,  
                        "std_change": self.stdev.set,
                        "events_plot": self.proteinInfoPlot,
                        "freq_change": self.frame.set
                        } 
        #f.close()
        self.isAnlysis = False
        self.npassist = None
        self.dI_single = None
        self.eventsanalysis = None
        self.setprotocol()
        self.subwindow.destroy()


    def setcurrent(self, current):
        self.current.set(current) 
        if self.npassist:
            self.npassist.calradiuslength(current)   
            self.dI_single = self.npassist.getdI()   

    def proteinInfoPlot(self, nanopore_events):
        if not self.eventsanalysis:
            return 
        self.eventsanalysis.proteinInfoPlot(nanopore_events)
        return

    def currentPlot(self, ydata, eventlist):
        if self.dI_single:
            eventlist[2] = [ydata[0][0], ydata[0][-1]]
            di = self.current.get()-self.dI_single
            eventlist[3] = [di, di]
        self.display.append(ydata, eventlist) 
        freq = round((time.time() - self.time_start) * 1000, 0) 
        self.speed.set(f'{freq} ms')
        self.time_start = time.time() 


    def filter(self):
        filter = self.lp.get()
        self.que_write.put(('setfilter', filter), True)

    def showAnalysis(self):
        self.isAnlysis = True
        analysiswindow = tk.Toplevel(self.root) 
        self.eventsanalysis = EventsAnalysis(analysiswindow, self.que_write)
        analysiswindow.bind('<Destroy>', self.destroyAnalysisWindow)

    def destroyAnalysisWindow(self, event):
        self.eventsanalysis = None

    def setxwindow(self):
        xwindow = self.xwindow.get()
        if xwindow < 1:
            self.root.focus()
            return
        self.que_write.put(('setwindow', xwindow), True)
        self.display.setxlim(float(self.xwindow.get()))
        self.root.focus()
        

    def home(self):
        current = self.current.get()
        stdev = self.stdev.get()
        newlim = [current-int(self.th.get())*stdev, current+int(self.th.get())*stdev]
        self.display.setylim(newlim)
        self.root.focus()
    
    def setylim(self, event):
        y1 = float(self.y1.get())
        y2 = float(self.y2.get())
        self.display.setylim([y2, y1])
        self.root.focus()

    def openfolder(self): 
        self.foldername.set(tk.filedialog.askdirectory())
        
    def flush(self):
        self.que_write.put(('flush', None), True)

    def apply(self):
        voltage = self.voltage.get()
        voltage = 1000 if voltage > 1000 else voltage
        voltage = -1000 if voltage < -1000 else voltage
        self.que_write.put(('setvoltage', voltage), True)


    def play(self):
        if self.playbutton['text'] == 'Stop':
            self.playbutton.configure(text = 'Play')
            self.que_write.put(None, True)
            return 
        self.playbutton.configure(text = 'Stop')

        parameter = {}
        for key, value in self.ParameterVar.items():
            parameter[key] = value.get()
        parameter['mode'] = self.protocol_mode.get()
        if parameter['mode'] == 'gapfree' or parameter['mode'] == 'sweep':
            parameter['Vichannel'] = parameter['Vichannel']  if parameter['Vichannel'] else None
            parameter['Vochannel'] = parameter['Vochannel'] if parameter['Vochannel'] else None
        parameter['filter'] = self.lp.get()
        parameter['window'] = self.xwindow.get()
        parameter["filename"] = None
        self.que_write.put(parameter, True)
        while True:
            buffer = self.que_read.get(True)
            if not buffer:
                break
            if buffer[0] in self.obj_slot.keys():
                self.obj_slot[buffer[0]](*buffer[1])
        if self.playbutton['text'] == 'Stop':
            self.playbutton.configure(text = 'Play')
        return 

    
    def record(self):
        if self.recordbutton['text'] == 'Stop':
            self.recordbutton['text'] = 'Record'
            self.playbutton['state'] = 'normal'
            self.que_write.put(('setfilename', None), True)
            return 
        if self.playbutton['text'] == 'Play':
            return
        self.playbutton['state'] = 'disable'
        self.recordbutton['text'] = 'Stop'
        fs = self.ParameterVar['fs'].get()
        filename = self.foldername.get()+'/'+self.filename.get() + f'_{fs}kHz_' + self.protocol_mode.get()
        self.que_write.put(('setfilename', filename), True)
            
    def setprotocol(self):
        self.subwindow = tk.Toplevel(self.root) 
        self.subwindow.geometry('200x800')
        self.combobox_protocal = ttk.Combobox(self.subwindow, textvariable=self.protocol_mode) 
        self.combobox_protocal["values"] = ["gapfree", "sweep", "test", "simulate"]
        self.combobox_protocal.place(x = 10, y = 10, width=180, height=30)
        self.combobox_protocal['state'] = 'readonly' 
        self.combobox_protocal.set('gapfree')
        self.combobox_protocal.bind("<<ComboboxSelected>>", self._loadjson)
        self._loadjson(None)

    def _loadjson(self, event):
        jsonfile = "./src/protocol.json"
        mode = self.protocol_mode.get()
        position = 50
        for widget in self.subwindow.winfo_children():
            if widget != self.combobox_protocal:
                widget.destroy()
        with open(jsonfile) as f:
            data = json.load(f)
            for key, value in data[mode].items():
                if isinstance(value, int):
                    self.ParameterVar[key] = tk.IntVar()
                    self.ParameterVar[key].set(value)
                    tk.Label(self.subwindow, text = key).place(x = 10, y = position, width = 100, height = 30) 
                    tk.Entry(self.subwindow, textvariable=self.ParameterVar[key]).place(x = 120, y = position, width = 70, height = 30)
                elif isinstance(value, float):
                    self.ParameterVar[key] = tk.DoubleVar()
                    self.ParameterVar[key].set(value)
                    tk.Label(self.subwindow, text = key).place(x = 10, y = position, width = 100, height = 30) 
                    tk.Entry(self.subwindow, textvariable=self.ParameterVar[key]).place(x = 120, y = position, width = 70, height = 30)
                else:
                    self.ParameterVar[key] = tk.StringVar()
                    self.ParameterVar[key].set(value)
                    tk.Label(self.subwindow, text = key).place(x = 10, y = position, width = 100, height = 30) 
                    tk.Entry(self.subwindow, textvariable=self.ParameterVar[key]).place(x = 120, y = position, width = 70, height = 30)
                position += 40 

    def destroyAssistWindow(self, event):
        self.npassist = None
        self.dI_single = None

    def nanoporecalculator(self):
        root= tk.Toplevel(self.root)
        self.npassist = NanoporeAssist(root)
        root.bind('<Destroy>', self.destroyAssistWindow)






if __name__ == '__main__': 
    parent_que, child_que = Queue(), Queue()
    p = Process(target = startserver, args = ((child_que, parent_que)))
    p.start()
    root = tk.Tk()
    
    daq = DaqGui(root, parent_que, child_que)
    root.mainloop()

