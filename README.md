# pydaq3
a python/cpp software for data acquisition on NIDAQ card. multithreads, fast, real-time analysis.  
## features

![image](https://github.com/user-attachments/assets/2e6b9556-d550-4136-9c2f-7c4942fba7ab)   
1. data acquisition
2. real time peak detection. The program can process single point as a minimium input unit. but the normal WINDOWS operating system will have very large delay (1 - 10 ms).
3. analysis the shape and volume of proteins during the recording.
![image](https://github.com/user-attachments/assets/26bb6db7-0404-4952-a6ea-8989343a4d61)  
4. optimized visualization, used several method to improve the render speed.

## dependency
1. numpy, matplotlib, nidaqmx
2. there is a python dynamic lib, cfunction.pyd, which is compiled using pybind11, so unluckly, this can only run on python 3.7.
3. this file provides the real-time events detection.   
in the future, i will compile it to .dll.

## other function  
1. pydaq can generate simulation data,
2. play the recordered data
3. a lot of sweep mode for data acquisition (e.g., iv curve, various voltage wave)
4. provides a calculator, so that we can easily calculate the pore or protien properties during recording. the programm will read the baseline auto

## how to use  
1. make sure you lab pc have python 3.7 (have numpy, matplotlib). install the dependency, read the help.pdf
2. connect the cable to the axon and data acquisition card(NI)
3. choose the correct channel name, include current read channel ("Dev1/ai0", thoes are the device name and the BNC port name), voltage read or write  channel
