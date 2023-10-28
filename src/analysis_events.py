import tkinter as tk 
from tkinter import ttk
from PIL import Image, ImageTk


class EventsAnalysis:
    def __init__(self, root: tk.Tk, que_write = None) -> None:
        self.analysiswindow = root
        self.analysiswindow.title("Events Monitor") 
        self.analysiswindow.geometry("300x400")
        #self.analysiswindow.withdraw()
        self.image = tk.Label(self.analysiswindow, text = 'Protein Translocation Events Analysis')
        self.image.place(x = 0, y = 100, width=300, height = 300)
        self.length = tk.DoubleVar()
        self.length.set(30) 
        self.diameter = tk.DoubleVar() 
        self.diameter.set(20) 
        self.resistivity = tk.DoubleVar()
        self.resistivity.set(0.046) 
        self.voltage = tk.DoubleVar()
        self.voltage.set(-0.1) 
        self.analysis_id = tk.StringVar() 
        self.combobox = ttk.Combobox(self.analysiswindow, textvariable=self.analysis_id) 
        self.combobox["values"] = ["dt", "dI", "shape_o_rt", "shape_p_rt", "volume_o_rt", "volume_p_rt"]
        self.combobox.place(x = 10, y = 90, width=100, height=30)
        self.combobox['state'] = 'readonly' 
        self.combobox.set('shape_o_rt')
        self.combobox.bind("<<ComboboxSelected>>", self.setAnalysisID)
        self.que_write = que_write
        tk.Label(self.analysiswindow, text = 'lp(nm):').place(x=10, y = 10, width = 70, height = 30)
        tk.Entry(self.analysiswindow, textvariable=self.length).place(x=80, y = 10, width = 70, height = 30)
        tk.Label(self.analysiswindow, text = 'dp(nm):').place(x=150, y = 10, width = 70, height = 30)
        tk.Entry(self.analysiswindow, textvariable=self.diameter).place(x=220, y = 10, width = 70, height = 30)
        tk.Label(self.analysiswindow, text = 'resistivity:').place(x=10, y = 50, width = 70, height = 30)
        tk.Entry(self.analysiswindow, textvariable=self.resistivity).place(x=80, y = 50, width = 70, height = 30)
        tk.Label(self.analysiswindow, text = 'voltage(V):').place(x=150, y = 50, width = 70, height = 30)
        tk.Entry(self.analysiswindow, textvariable=self.voltage).place(x=220, y = 50, width = 70, height = 30)
        tk.Button(self.analysiswindow, text = 'ok', command=self.setAnalysisParameter).place(x=120, y = 90, width = 70, height = 30)

    def proteinInfoPlot(self, img_buffer):
        img = Image.open(img_buffer)
        photo = ImageTk.PhotoImage(img) 
        self.image.configure(image = photo) 
        self.image.image = photo
        return
    
    def setAnalysisID(self, events):
        self.analysiswindow.focus()
        self.que_write.put(('setanalysisid', self.combobox.get()), True)

    def setAnalysisParameter(self):
        self.que_write.put(('setnanopore', [self.diameter.get()*1e-9, self.length.get()*1e-9, self.resistivity.get(), self.voltage.get()]), True)
    

if __name__ == '__main__': 
    root = tk.Tk()
    EventsAnalysis(root)
    root.mainloop()