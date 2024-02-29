import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter, freqz




class signalAnalysis():
    def __init__(self,data,header, t):
        self.t = t
        for i, name in enumerate(header):
            if 'T1_' in name:
                indexTcell1 = i
            elif 'T2_' in name:
                indexTcell2 = i
            elif 'T3_' in name:
                indexTchamber = i
            elif 'Spannung 1' in name:
                indexVcell1 = i
            elif 'Spannung 2' in name:
                indexVcell2 = i

        self.Vdrop_cell1 = data[indexVcell1]
        self.Vdrop_cell2 = data[indexVcell2]
        self.Tcell1 = data[indexTcell1]
        self.Tcell2 = data[indexTcell2]
        self.T_chamber = data[indexTchamber]


        self.maxT()
        self.tVdrop()


    def butter_lowpass(self, cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def maxT(self):
        self.maxTcell1 = np.max(self.Tcell1)
        self.maxTcell2 = np.max(self.Tcell2)
        self.maxT_chamber = np.max(self.T_chamber)

    def tVdrop(self):
        self.Vdrop_filter = self.butter_lowpass_filter(self.Vdrop_cell1, 0.01,10,5)
        self.grad = np.gradient(self.Vdrop_filter)
        index = np.where(self.grad == np.min(self.grad))
        self.timeVdrop_cell1 = (self.t[index][0])

        self.Vdrop_filter = self.butter_lowpass_filter(self.Vdrop_cell2, 0.01,10,5)
        self.grad = np.gradient(self.Vdrop_filter)
        index = np.where(self.grad == np.min(self.grad))
        self.timeVdrop_cell2 = (self.t[index][0])




