from multiprocessing import Queue
import nidaqmx 
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogSingleChannelWriter
from nidaqmx.constants import AcquisitionType, OverwriteMode
import numpy as np 
import time 
from ._math import GenerateWave
from ._datahandle import DaqIOHandle, DaqDataHandle, DaqFitHandle
from ._poresimulator import NanoporeSimulator

def startserver(que_read : Queue, que_write : Queue):
    while True:
        parameter = que_read.get(True)
        if parameter == 'Stop':
            print('close connection')
            break
        if isinstance(parameter, dict):
            server = DataDaq(que_read, que_write, parameter)
            print('data acquisition protocol start: ' + f'{parameter}')
            if hasattr(server, parameter['mode']):
                func = getattr(server, parameter['mode'])
                func()
    que_read.close()

class DataDaq:
    def __init__(self, que_read : Queue, que_write : Queue, parameter: dict) -> None:
        self.handle_data = None 
        self.handle_fit = None 
        self.handle_io = None
        self.slot = {'setfilter': self._setFilter,
                    'flush':self._flush, 
                    'reset':self._reset, 
                    'setwindow':self._setWindow, 
                    'setfilename': self._setFilename,
                    'setnanopore':self._setNanopore,
                    'setanalysisid':self._setAnalysisID,
                    'setvoltage': self._setVoltage}
        self.que_write = que_write 
        self.que_read = que_read 
        self.parameter = parameter 
        self.v = None
        return 
    
    def _setFilter(self, filter):
        self.handle_data.setfilter(filter) 

    def _flush(self, p = None):
        self.handle_data.flush() 

    def _reset(self, p = None):
        self.handle_data.reset() 
        self.handle_io.reset() 
        self.handle_fit.reset()

    def _setWindow(self, window):
        self.handle_data.setwindow(window) 

    def _setFilename(self, filename):
        self.handle_data.reset() 
        self.handle_io.setfile(filename)
        self.handle_fit.reset()

    def _setNanopore(self, para):
        self.handle_fit.setnanopore(para)
    
    def _setAnalysisID(self, id):
        self.handle_fit.setanalysisid(id)

    def _setVoltage(self, v):
        if self.writer is None or self.parameter['mode'] != 'gapfree':
            return 
        self.writer.write_one_sample(v / 100)
        self.handle_io.setfilenamebyvoltage(v)
        self.handle_data.reset()
        self.v = np.zeros(1, 'float64') + v 


    def test(self):
        v = np.zeros(1, 'float64')
        data_pointer = np.memmap("./src/Data_CH003_000_17sto207s.dat", dtype='float32')
        i=0
        self.handle_data = DaqDataHandle(self.parameter['fs'], self.parameter['filter'], self.parameter['window'], \
                                         self.parameter['threshold'], self.parameter['direction'], self.parameter['windowbaseline'], \
                                            self.parameter['windowending'])
        self.handle_io = DaqIOHandle(self.parameter['filename'], 0)
        self.handle_fit = DaqFitHandle(20e-9, 30e-9, 0.046, -0.2, self.que_write)
        Nfile = int(self.parameter['filetime'] * 50) 
        N = 0
        while True:
            try:
                s = self.que_read.get_nowait()   
                if s is None:
                    self.que_write.put(None, True)
                    self.handle_io.close()
                    break 
                elif isinstance(s, tuple):
                    self.slot[s[0]](s[1])
            except:
                pass
        
            if i == 1000:
                i=0
            time.sleep(0.02)
            data = data_pointer[i*10000:i*10000+10000].reshape(1,-1)
            a=time.time()
            res = self.handle_data.process(data)
            self.handle_fit.append(data, res.eventstring, res.flag)
            self.handle_io.append(data, v)            
            i+=1
            self.handle_io.appendevent(res.eventstring)
            try:
                self.que_write.put_nowait(("current_plot", (res.data, res.event))) 
              
                if i%20==0:
                    self.que_write.put_nowait(("mean_change", [round(res.mean, 1)]))   
                    self.que_write.put_nowait(("std_change", [round(res.stdev, 1)]))   
            except:
                pass
            N += 1 
            if N == Nfile:
                N = 0
                self._reset()
        print(f'total time: {i * 0.02} s')

    def gapfree(self):
        writemode = 0
        if self.parameter['Vichannel'] is not None:
            writemode = 1
        self.handle_data = DaqDataHandle(self.parameter['fs'], self.parameter['filter'], self.parameter['window'], \
                                         self.parameter['threshold'], self.parameter['direction'], self.parameter['windowbaseline'], \
                                            self.parameter['windowending'])
        self.handle_io = DaqIOHandle(self.parameter['filename'], writemode)
        self.handle_fit = DaqFitHandle(20e-9, 30e-9, 0.046, -0.2, self.que_write)
        samplingrate = self.parameter['fs']
        ab = self.parameter['ab']
        arraysize= int(samplingrate * 20)
        row = 2 if self.parameter['Vichannel'] is not None else 1
        data = np.zeros((row, arraysize), 'float64')
        with nidaqmx.Task() as task_read, nidaqmx.Task() as task_write:
            if self.parameter['Vochannel'] is not None:
                task_write.ao_channels.add_ao_voltage_chan(self.parameter['Vochannel'])
                #task_write.timing.cfg_samp_clk_timing(parameter['fs']*2, sample_mode=AcquisitionType.CONTINUOUS)
                self.writer = AnalogSingleChannelWriter(task_write.out_stream) 
                task_write.start()
            task_read.ai_channels.add_ai_voltage_chan(self.parameter['Iichannel'], min_val = -10, max_val=10)
            task_read.timing.cfg_samp_clk_timing(samplingrate*1000, sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=arraysize)
            task_read.in_stream.over_write = OverwriteMode.DO_NOT_OVERWRITE_UNREAD_SAMPLES
            if row == 2:
                task_read.ai_channels.add_ai_voltage_chan(self.parameter['Vichannel'], min_val = -10, max_val=10)
            reader = AnalogMultiChannelReader(task_read.in_stream) 
            i = 0
            Nfile = int(self.parameter['filetime'] * 50) 
            N = 0
            task_read.start()
            while True:
                i += 1   
                try:
                    s = self.que_read.get_nowait()   
                    if s is None:
                        self.que_write.put(None, True)
                        self.handle_io.close()
                        break 
                    elif isinstance(s, tuple):
                        self.slot[s[0]](s[1]) 
                except:
                    pass
                #randf()
                reader.read_many_sample(data, number_of_samples_per_channel=arraysize)
                data[0][:] = data[0] * 1000 / ab
                if row == 2:
                    data[1][:] = data[1] * 100 
                res = self.handle_data.process(data)
                self.handle_fit.append(data, res.eventstring, res.flag)
                self.handle_io.append(data, self.v) 
                self.handle_io.appendevent(res.eventstring)
                try:
                    self.que_write.put_nowait(("current_plot", (res.data, res.event))) 
              
                    if i%10==0:
                        self.que_write.put_nowait(("mean_change", [round(res.mean, 1)]))   
                        self.que_write.put_nowait(("std_change", [round(res.stdev, 1)]))   
                except:
                    pass
                N += 1 
                if N == Nfile:
                    N = 0
                    self._reset()
            if self.writer is not None:
                self.writer.write_many_sample(np.zeros((20,), dtype='float64'))
                time.sleep(0.1)
                task_write.stop()
            task_read.stop()
        print(f'total time: {i * 0.02} s')

    def sweep(self):
        writemode = 2
        if self.parameter['Vichannel'] is not None:
            writemode = 1
        self.handle_data = DaqDataHandle(self.parameter['fs'], self.parameter['filter'], self.parameter['window'], \
                                         self.parameter['threshold'], self.parameter['direction'], self.parameter['windowbaseline'], \
                                            self.parameter['windowending'])
        self.handle_io = DaqIOHandle(self.parameter['filename'], writemode)
        self.handle_fit = DaqFitHandle(20e-9, 30e-9, 0.046, -0.2, self.que_write)
        samplingrate = self.parameter['fs']
        ab = self.parameter['ab']
        arraysize= int(samplingrate * 20)
        row = 2 if self.parameter['Vichannel'] is not None else 1
        data = np.zeros((row, arraysize), 'float64')
        generator = GenerateWave(self.parameter['period'], 1000, self.parameter['lagtime'], self.parameter['increment'],\
                                self.parameter['amplitude'], self.parameter['v0'], self.parameter['maxvoltage'], \
                                self.parameter['wave'])
        with nidaqmx.Task() as task_read, nidaqmx.Task() as task_write:
            task_write.ao_channels.add_ao_voltage_chan(self.parameter['Vochannel'])
            #task_write.timing.cfg_samp_clk_timing(1000, sample_mode=AcquisitionType.CONTINUOUS)
            self.writer = AnalogSingleChannelWriter(task_write.out_stream) 
            task_write.start()
            task_read.ai_channels.add_ai_voltage_chan(self.parameter['Iichannel'], min_val = -10, max_val=10)
            task_read.timing.cfg_samp_clk_timing(samplingrate*1000, sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=arraysize)
            task_read.in_stream.over_write = OverwriteMode.DO_NOT_OVERWRITE_UNREAD_SAMPLES
            if row == 2:
                task_read.ai_channels.add_ai_voltage_chan(self.parameter['Vichannel'], min_val = -10, max_val=10)
            reader = AnalogMultiChannelReader(task_read.in_stream) 
            i = 0
            Nfile = int(self.parameter['filetime'] * 50) 
            N = 0
            task_read.start()
            while True:
                i += 1   
                try:
                    s = self.que_read.get_nowait()   
                    if s is None:
                        self.que_write.put(None, True)
                        self.handle_io.close()
                        break 
                    elif isinstance(s, tuple):
                        self.slot[s[0]](s[1]) 
                except:
                    pass
                #randf()
                reader.read_many_sample(data, number_of_samples_per_channel=arraysize)
                data[0][:] = data[0] * 1000 / ab
                if row == 2:
                    data[1][:] = data[1] * 100 
                res = self.handle_data.process(data)
                v = generator.get()
                self.handle_io.append(data, v)
                self.writer.write_many_sample(v / 100)
                try:
                    self.que_write.put_nowait(("current_plot", (res.data, res.event))) 
              
                    if i%10==0:
                        self.que_write.put_nowait(("mean_change", [round(res.mean, 1)]))   
                        self.que_write.put_nowait(("std_change", [round(res.stdev, 1)]))   
                except:
                    pass
                N += 1 
                if N == Nfile:
                    N = 0
                    self._reset()
            if self.writer is not None:
                self.writer.write_many_sample(np.zeros((20,), dtype='float64'))
                time.sleep(0.1)
                task_write.stop()
            task_read.stop()
        print(f'total time: {i * 0.02} s')

    def simulate(self):
        self.handle_data = DaqDataHandle(500, self.parameter['filter'], self.parameter['window'], \
                                         self.parameter['threshold'], self.parameter['direction'], self.parameter['windowbaseline'], \
                                            self.parameter['windowending'])
        self.handle_io = DaqIOHandle(self.parameter['filename'], 0)
        self.handle_fit = DaqFitHandle(20e-9, 30e-9, 0.046, -0.2, self.que_write)
        v = np.zeros(1, 'float64')
        simulator = NanoporeSimulator() 
        simulator.addProtein() 
        i = 0
        for data in simulator.simulateAcquisition3D(500000, 100):
            i += 1
            try:
                s = self.que_read.get_nowait()   
                if s is None:
                    self.que_write.put(None, True)
                    self.handle_io.close()
                    break 
                elif isinstance(s, tuple):
                    self.slot[s[0]](s[1])
            except:
                pass
            data = data.reshape(1,-1)
            time.sleep(0.02)
            res = self.handle_data.process(data)
            self.handle_fit.append(data, res.eventstring, res.flag)
            self.handle_io.append(data, v)
            self.handle_io.appendevent(res.eventstring)
            try:
                self.que_write.put_nowait(("current_plot", (res.data, res.event))) 
                if i%10==0:
                    self.que_write.put_nowait(("mean_change", [round(res.mean, 1)]))   
                    self.que_write.put_nowait(("std_change", [round(res.stdev, 1)]))   
            except:
                pass    