from matplotlib.axes import Axes 



class DisplayRealTime():
    def __init__(self, ax:Axes, xwindow, ywindow, frame = 50):
        self.ax = ax
        self.ax.plot(0, 0, animated = True, linewidth = 1, color = 'black')
        self.ax.plot(0, 0, animated = True, linewidth = 0.5, color = "red")
        self.ax.plot(0, 0, animated = True, linewidth = 0.5, color = "green") 
        self.ax.locator_params(axis = 'both', nbins = 5)
        self.line = ax.lines
        self.fig = ax.figure
        self.xwindow = xwindow
        self.ywindow = ywindow
        self.interval = 1 / frame
        self.ax.set_xlabel("Time s")
        self.ax.set_ylabel("Current pA")
        self.ax.set_xlim([0, self.xwindow])
        self.ax.set_ylim(self.ywindow)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        self.bg = ax.figure.canvas.copy_from_bbox(ax.figure.bbox)
        self.xlim = [0, xwindow]


    def append(self, ydata:list, event:list):
        if ydata[0][-1] < self.xlim[1] and ydata[0][0] > self.xlim[0]:  
            self.fig.canvas.restore_region(self.bg)
            self.line[0].set_data(ydata[0], ydata[1]) 
            self.line[1].set_data(event[0], event[1]) 
            self.line[2].set_data(event[2], event[3])
            self.ax.draw_artist(self.line[0]) 
            self.ax.draw_artist(self.line[1]) 
            self.ax.draw_artist(self.line[2]) 
            self.fig.canvas.blit(self.fig.bbox)
            self.fig.canvas.flush_events()    
        else:
            self.xlim = [ydata[0][0], ydata[0][0] + self.xwindow]
            self.line[0].set_data(ydata[0], ydata[1]) 
            self.line[1].set_data(event[0], event[1]) 
            self.ax.set_xlim(self.xlim) 
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        self.bg = self.ax.figure.canvas.copy_from_bbox(self.ax.figure.bbox)


    def setxlim(self, xwindow):
        self.xwindow = xwindow 
        self.xlim = [self.xlim[0], self.xlim[0]+xwindow]
        self.ax.set_xlim(self.xlim) 
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def setylim(self, ywindow):
        self.ywindow = ywindow 
        self.ax.set_ylim(ywindow) 
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()        

        