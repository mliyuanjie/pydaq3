import numpy as np 
import tkinter as tk 
from tkinter import ttk

class nanoporeCalculator:
    def __init__(self, dpore, lpore, kcl, voltage, volume, shape) -> None:
        self.dpore = dpore 
        self.lpore = lpore 
        self.resistivity = kcl 
        self.voltage = voltage 
        self.volume = volume 
        self.shape = shape
        self.calbaseline()
        self.calIminImax()

        

    def calIminImax(self, volume = None, shape = None):
        self.volume = volume if volume is not None else self.volume
        self.shape = shape if shape is not None else self.shape 
        if self.shape <= 1:
            m2 = self.shape * self.shape
            self.yfactor = 1/(self.shape*np.arccos(self.shape)/np.power(1-m2,1.5)-m2/(1-m2))
            self.Imax = self.volume * (self.g * self.yfactor * self.baseline)
            self.Imin = self.Imax / (self.yfactor - 0.5)     
        else:
            m2 = self.shape * self.shape
            self.yfactor = 1/(m2/(m2-1)-self.shape*np.arccosh(self.shape)/np.power(m2-1, 1.5))
            self.Imin = self.volume * (self.g * self.yfactor * self.baseline)
            self.Imax = self.Imin / (self.yfactor - 0.5)

    def calbaseline(self, dpore = None, lpore = None, voltage = None, kcl = None):
        pi = 3.141592653
        self.dpore = dpore if dpore is not None else self.dpore
        self.lpore = lpore if lpore is not None else self.lpore 
        self.voltage = voltage if voltage is not None else self.voltage 
        self.resistivity = kcl if kcl is not None else self.resistivity 
        self.baseline = self.voltage / (self.resistivity / (2 * self.dpore) + (self.resistivity * self.lpore) / (pi * self.dpore * self.dpore))
        self.efield = self.voltage *(self.resistivity * self.lpore /(pi * self.dpore * self.dpore)) \
        / (self.resistivity * self.lpore / (pi * self.dpore * self.dpore) + self.resistivity \
        / (2 * self.dpore)) / self.lpore
        self.g = 1/(pi * self.dpore * self.dpore * (self.lpore + 1.6 * self.dpore))

    def caldpore(self, baseline = None):
        if baseline is None:
            return 
        pi = 3.141592653
        self.baseline = baseline
        temp = np.sqrt(pi/(16*self.lpore)+self.voltage/(baseline*self.resistivity))-np.sqrt(pi/(16*self.lpore))
        self.dpore = np.sqrt(self.lpore/pi)/temp 
        self.efield = self.voltage *(self.resistivity * self.lpore /(pi * self.dpore * self.dpore)) \
        / (self.resistivity * self.lpore / (pi * self.dpore * self.dpore) + self.resistivity \
        / (2 *self.dpore)) / self.lpore
        self.g = 1/(pi * self.dpore * self.dpore * (self.lpore + 1.6 * self.dpore))
        self.calIminImax()

    def callpore(self, baseline = None):
        if baseline is None:
            return 
        pi = 3.141592653
        self.baseline = baseline
        self.lpore = (self.voltage/self.baseline-self.resistivity/(2*self.dpore))*(pi*self.dpore*self.dpore)/self.resistivity
        self.efield = self.voltage *(self.resistivity * self.lpore /(pi * self.dpore * self.dpore)) \
        / (self.resistivity * self.lpore / (pi * self.dpore * self.dpore) + self.resistivity \
        / (2 *self.dpore)) / self.lpore
        self.g = 1/(pi * self.dpore * self.dpore * (self.lpore + 1.6 * self.dpore))
        self.calIminImax()
        
        

        
class NanoporeAssist():
    def __init__(self, root: tk.Tk):
        #main window initialize
        self.root = root 
        self.root.title('Nanopre Calculator')
        self.root.geometry('340x300')

        self.dpore = tk.DoubleVar()
        self.dpore.set('10')
        self.lpore = tk.DoubleVar()
        self.lpore.set('30')
        self.kcl = tk.DoubleVar()
        self.kcl.set('0.046')
        self.voltage = tk.DoubleVar()
        self.voltage.set('-0.1')
        self.baseline = tk.DoubleVar()
        self.baseline.set('0')
        self.shape = tk.DoubleVar()
        self.shape.set('0.6')
        self.volume = tk.DoubleVar()
        self.volume.set('100')

        self.fixpara = tk.StringVar()
        self.number = tk.StringVar()
        self.number.set('0')
        
        self.baseline = tk.DoubleVar()
        self.baseline.set('10')
        self.Imin = tk.DoubleVar()
        self.Imin.set('10')
        self.Imax = tk.DoubleVar()
        self.Imax.set('10')

        self.rms = tk.DoubleVar()
        self.rms.set('50')
        self.dm = tk.DoubleVar()
        self.dm.set('1')
        


        tk.Label(self.root, text="Pore Radius(nm)").place(x=10, y = 10, width = 100, height = 30)
        e1 = tk.Entry(self.root, textvariable=self.dpore)
        e1.bind('<Return>', self.calbaseline)
        e1.place(x=120, y = 10, width = 40, height = 30)
        
        tk.Label(self.root, text="Pore Length(nm)").place(x=180, y = 10, width = 100, height = 30)
        e2 = tk.Entry(self.root, textvariable=self.lpore)
        e2.bind('<Return>', self.calbaseline)
        e2.place(x=290, y = 10, width = 40, height = 30)

        tk.Label(self.root, text="KCL(omi)").place(x=10, y = 60, width = 100, height = 30)
        e1 = tk.Entry(self.root, textvariable=self.kcl)
        e1.bind('<Return>', self.calbaseline)
        e1.place(x=120, y = 60, width = 40, height = 30)

        tk.Label(self.root, text="Voltage(V)").place(x=180, y = 60, width = 100, height = 30)
        e2 = tk.Entry(self.root, textvariable=self.voltage)
        e2.bind('<Return>', self.calbaseline)
        e2.place(x=290, y = 60, width = 40, height = 30)

        tk.Label(self.root, text="Baseline(nA)").place(x=10, y = 110, width = 100, height = 30)
        e1 = tk.Label(self.root, textvariable=self.baseline)
        e1.place(x=110, y = 110, width = 100, height = 30)

        e1 = ttk.Combobox(self.root, textvariable=self.fixpara)
        e1['values'] = ["radius free", "length free"]
        e1.current(0)
        e1.place(x=210, y = 110, width = 120, height = 30)

        tk.Label(self.root, text="Shape").place(x=10, y = 160, width = 100, height = 30)
        e1 = tk.Entry(self.root, textvariable=self.shape)
        e1.bind('<Return>', self.calIminImax)
        e1.place(x=120, y = 160, width = 40, height = 30)
        

        tk.Label(self.root, text="Volume(nm3)").place(x=180, y = 160, width = 100, height = 30)
        e1 = tk.Entry(self.root, textvariable=self.volume)
        e1.bind('<Return>', self.calIminImax)
        e1.place(x=290, y = 160, width = 40, height = 30)

        tk.Label(self.root, text="Imin(pA)").place(x=10, y = 210, width = 100, height = 30)
        e1 = tk.Label(self.root, textvariable=self.Imin)
        e1.place(x=120, y = 210, width = 40, height = 30)

        tk.Label(self.root, text="Imax(pA)").place(x=180, y = 210, width = 100, height = 30)
        e1 = tk.Label(self.root, textvariable=self.Imax)
        e1.place(x=290, y = 210, width = 40, height = 30)

        self.calculator = nanoporeCalculator(10e-9, 30e-9, 0.046, -0.1, 100e-27, 0.6)
        self.Imin.set(round(self.calculator.Imin * 1e12,1)) 
        self.Imax.set(round(self.calculator.Imax * 1e12,1))
    
    def calbaseline(self, event):
        dpore = self.dpore.get()*1e-9 
        lpore = self.lpore.get()*1e-9 
        voltage = self.voltage.get()
        kcl = self.kcl.get() 
        self.calculator.calbaseline(dpore, lpore, voltage, kcl)
        self.calIminImax(None)

    def calIminImax(self, event):
        shape = self.shape.get()
        volume = self.volume.get()*1e-27
        self.calculator.calIminImax(volume,shape)
        self.Imin.set(round(self.calculator.Imin * 1e12,1)) 
        self.Imax.set(round(self.calculator.Imax * 1e12,1))

    def calradiuslength(self, baseline):
        self.baseline.set(round(baseline * 1e-3,1))
        if self.fixpara.get() == "radius free": 
            self.calculator.caldpore(baseline*1e-12) 
            self.dpore.set(round(self.calculator.dpore*1e9,1))
        elif self.fixpara.get() == "length free":
            self.calculator.callpore(baseline*1e-12)
            self.lpore.set(round(self.calculator.lpore*1e9,1))
        self.Imin.set(round(self.calculator.Imin * 1e12,1)) 
        self.Imax.set(round(self.calculator.Imax * 1e12,1))

    def getdI(self):
        return (self.Imin.get() + self.Imax.get())/2

if __name__ == '__main__': 
    root = tk.Tk()
    NanoporeAssist(root)
    root.mainloop()


