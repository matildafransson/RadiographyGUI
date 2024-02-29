# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 14:12:00 2022

@author: PfaffJ
"""

import h5py
from pylab import *

import tpc5

class importTPC5():
    """
    Class to import tcp5 file data
    """

    def __init__(self,pathTPC5):
        self.pathToTPC5 = pathTPC5
        print('Loading Transcom Data')
        self.loadFile()

    def loadFile(self):
        self.f  = h5py.File(self.pathToTPC5, "r")

    def closeFile(self):
        self.f.close()

    def getDatasets(self):
        
        channelName = '/measurements/00000001/channels/'
    
        group_obj = self.f[channelName]

        num_channels = size(list(group_obj))
        num_array = list(range(1,num_channels+1))

        list_names = ['- Select data -']
        for idx in num_array:
            chName = tpc5.getChannelName(self.f, idx)
            list_names.append(chName)
            
        return list_names
    
    def getData(self,idx):

        chName = tpc5.getChannelName(self.f, idx)
        TriggerSample = tpc5.getTriggerSample(self.f,idx,1)
        SamplingRate  = tpc5.getSampleRate(self.f,idx,1)
        nSamples = size(tpc5.getPhysicalData(self.f,idx))
        physicalUnit = tpc5.getPhysicalUnit(self.f,idx)
        dataset1 = tpc5.getVoltageData(self.f,idx)
        
        unit = '[ ' + physicalUnit + ' ]'
        ''' Scale x Axis to ms '''
        TimeScale = 1000
        
        startTime = -TriggerSample /SamplingRate * TimeScale
        endTime   = (len(dataset1)-TriggerSample)/SamplingRate * TimeScale
        t         = arange(startTime, endTime, 1/SamplingRate * TimeScale)


        
        return t,dataset1,chName, unit

    def getAllData(self):
        channelName = '/measurements/00000001/channels/'
        group_obj = self.f[channelName]

        num_channels = size(list(group_obj))

        chName = []
        physicalUnit = []
        data = []
        # dataset1 = []

        for idx in range(num_channels):
            chName.append(tpc5.getChannelName(self.f, idx + 1))
            TriggerSample = tpc5.getTriggerSample(self.f, idx + 1, 1)
            SamplingRate = tpc5.getSampleRate(self.f, idx + 1, 1)
            nSamples = size(tpc5.getPhysicalData(self.f, idx + 1))
            physicalUnit.append(tpc5.getPhysicalUnit(self.f, idx + 1))
            data.append(tpc5.getPhysicalData(self.f, idx + 1))
            # dataset1.append(tpc5.getVoltageData(f,idx+1))


        return chName, physicalUnit, data

    def getParams(self):
        channelName = '/measurements/00000001/channels/'
        group_obj = self.f[channelName]

        num_channels = size(list(group_obj))

        TriggerSample = tpc5.getTriggerSample(self.f, 1, 1)
        SamplingRate = tpc5.getSampleRate(self.f, 1, 1)
        nSamples = size(tpc5.getPhysicalData(self.f, 1))
        # dataset1.append(tpc5.getVoltageData(self.f,idx+1))


        return TriggerSample, SamplingRate, nSamples


