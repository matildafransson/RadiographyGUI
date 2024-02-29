# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 14:46:26 2022

@author: pfaffj, matilda, ludo
"""

import numpy as np
import sys
import math
import os
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QGroupBox, QFileDialog
from PyQt5.QtWidgets import QMessageBox as msgBox

from import_Tpc5 import importTPC5
from importXLSX import readXLSX
from imageDisplayWidget import ImageDisplayWidget
from readTrigger import readTrigger
from tempFileReader import tempTxtFileReader
from SliderAndLabel import SliderAndLabel
from XrayReader import XrayReader
from LineEditAndButton import LineEditAndButton
from signalAnalysis import signalAnalysis
from videoReader import VideoWidget
import yaml
import glob
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from scipy.signal import argrelextrema

sys.path.append("..")


class MainWindow(QWidget):
    """
    MainWindow of the GUI
    """
    init_text = "Waiting for state update..."
    def __init__(self, *args, **kwargs):
        super().__init__()

        self._path = os.path.dirname(os.path.abspath(__file__))
        self.readConfigFile()
        path_icon = self._path + self.config['Paths']['Logo']
        app_icon = QtGui.QIcon()

        app_icon.addFile(path_icon, QSize(60, 60))
        self.setWindowIcon(app_icon)

        '''define font for GroupBox'''
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)

        versionNr = str(self.config['General']['Version'])
        self.setWindowTitle('Data Visualization v' + versionNr)

        '''define Main Layout'''
        self.uiLayout()

        '''define Layout and Boxes for the plots'''
        self.uiPlotWindows(font)

        self.uiParam(font)

        self.uiData(font)

        self.uiStatus(font)

        self.setLayout(self.mainQGridLayout)

        self.showMaximized()

        self.show()

    @pyqtSlot(str)
    def readConfigFile(self):
        with open("config.yaml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def uiLayout(self):
        """
        define main grid layout
        """

        self.mainQGridLayout = QGridLayout(self)

        '''adjust size of different grid positions -> is implemented to make the Box/Space for the parameters smaller'''
        self.mainQGridLayout.setColumnStretch(0, 3)
        self.mainQGridLayout.setColumnStretch(1, 3)
        self.mainQGridLayout.setColumnStretch(2, 1)

    def uiPlotWindows(self, font):
        """
        Initialisation of all the main layout and widgets
        :param font: QFont
        :return:
        """

        '''create Box for X-ray image'''
        self.BoxXrayView = QGroupBox(self)
        self.BoxXrayView.setFont(font)
        self.BoxXrayView.setTitle("Xray data")

        '''create Box for transcom data'''
        self.BoxDataView = QGroupBox(self)
        self.BoxDataView.setFont(font)
        self.BoxDataView.setTitle("Transcom data")

        '''create Box for temperature data'''
        self.BoxTempView = QGroupBox(self)
        self.BoxTempView.setFont(font)
        self.BoxTempView.setTitle("Temperature data")

        '''add all this boxes to the mainGridLayout'''
        self.mainQGridLayout.addWidget(self.BoxXrayView, 0, 0, 1, 1)
        self.mainQGridLayout.addWidget(self.BoxDataView, 1, 0, 1, 1)
        self.mainQGridLayout.addWidget(self.BoxTempView, 0, 1, 1, 1)

        '''create vBox for data plot -> Layout inside the Box'''
        self.vboxData = QVBoxLayout(self)
        self.BoxDataView.setLayout(self.vboxData)

        '''predefine figure and plot empty canvas into vBoxLayout (Data)'''
        self.figure = matplotlib.figure.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.vboxData.addWidget(self.canvas)

        '''slider for transcom data'''
        self.sliderData = SliderAndLabel()
        self.sliderData._setRange(0, 0)
        self.vboxData.addWidget(self.sliderData)
        self.sliderData.slider.valueChanged.connect(self._dataSliderChanged)

        '''create vBox for image plot'''
        self.vboxImage = QVBoxLayout(self)
        self.BoxXrayView.setLayout(self.vboxImage)

        '''Widget to display stack of images with a slider to change image index and double slider to change contrast
        Button to go back to original size, and a button to go to the first frame display
        X-ray parameter givien to have default colormap in level of gray'''
        self.xRayVisu = ImageDisplayWidget('X-ray')
        self.vboxImage.addWidget(self.xRayVisu)

        self.vboxTemp = QVBoxLayout(self)

        ''' Temp Parameter to have a choose color map can be change in the tempColorMap file '''
        self.tempVisu = ImageDisplayWidget('Temp')
        self.vboxTemp.addWidget(self.tempVisu)

        self.BoxTempView.setLayout(self.vboxTemp)

        '''Signals to connect the sliders together, temp , xray and transcom data'''
        self.xRayVisu.imageVisualizer.sliceSlider.slider.valueChanged.connect(self._xRaySliderChanged)
        self.tempVisu.imageVisualizer.sliceSlider.slider.valueChanged.connect(self._tempSliderChanged)

        '''Connect visu button to the start of the images with the slider'''
        self.xRayVisu.toolBar.jumpbutton.clicked.connect(self.jumptoXray)
        self.tempVisu.toolBar.jumpbutton.clicked.connect(self.jumptoTemp)

    def _xRaySliderChanged(self, value):
        self.tempVisu.imageVisualizer.sliceSlider.slider.setValue(value)
        self.sliderData.slider.setValue(value)

    def _tempSliderChanged(self, value):
        self.xRayVisu.imageVisualizer.sliceSlider.slider.setValue(value)

    def _dataSliderChanged(self, value):
        """" Function to draw a vertical line on the transcom data when the slider is changed"""
        self.xRayVisu.imageVisualizer.sliceSlider.slider.setValue(value)
        self.vLine.remove()
        self.vLine = self.ax3.axvline(x=self.t[value], color="r")
        self.yvalue = self.data[self.indextranscom - 1][value]
        self.label.remove()
        self.label = self.ax3.text(np.min(self.t), np.max(self.data[self.indextranscom -1])*0.8,round(self.yvalue, 3))
        self.canvas.draw_idle()

    def jumptoXray(self):
        self.xRayVisu.imageVisualizer.sliceSlider.slider.setValue(self.delay_Xray)

    def jumptoTemp(self):
        self.xRayVisu.imageVisualizer.sliceSlider.slider.setValue(self.delay_TC)

    def uiStatus(self, font):
        """
        define Box and add Box to mainLayout
        :param font: QFont
        """
        self.BoxSettings = QGroupBox(self)
        self.BoxSettings.setFont(font)
        self.BoxSettings.setObjectName("BoxDataView")
        self.BoxSettings.setTitle("Settings")
        self.mainQGridLayout.addWidget(self.BoxSettings, 1, 2, 1, 1)

        '''create vBox for settings'''
        self.vboxSettings = QGridLayout(self)
        self.BoxSettings.setLayout(self.vboxSettings)

        self._textBox = QTextEdit(self)
        self._textBox.setReadOnly(True)
        self._textBox.setPlainText(self.init_text)

        ''' Line and Edit widget with a Button to select the working directory'''
        self.directoryW = LineEditAndButton()
        self.readConfigFile()
        self.directoryW.txtZone.setText(self.config['Paths']['MainPathExperiment'])
        self.directoryW.buttonDir.clicked.connect(self.dirClicked)

        ''' add dropdown menu for transcom data'''
        self._cbData = QComboBox(self)
        self._cbData.addItem('- Select data -')
        self._cbData.addItem('import data first!')
        self._cbData.setEnabled(False)

        '''link to "cbDataIndexChanged" function'''
        self._cbData.currentIndexChanged.connect(self.cbDataIndexChanged)

        '''define Buttons '''
        self._ButtonSave = QPushButton("Save", self)
        self._ButtonSave.setEnabled(False)
        # TODO Saving Data
        self._ButtonLoad = QPushButton("Import Data", self)
        self._ButtonLoad.clicked.connect(self.bLoadClicked)  # link button to function

        '''add all defined widget (Buttons, dropdown menu) to vBox'''
        self.vboxSettings.addWidget(self._textBox, 2, 0, 2, 2)
        self.vboxSettings.addWidget(self.directoryW, 0, 0, 1, 2)
        self.vboxSettings.addWidget(self._cbData, 1, 0, 1, 2)
        self.vboxSettings.addWidget(self._ButtonSave, 1, 2, 1, 4)
        self.vboxSettings.addWidget(self._ButtonLoad, 0, 2, 1, 4)

    def dirClicked(self):
        """
        Method to display a QFileDialog and display the path into the QLineEdit
        """

        dialog = QFileDialog(self, 'Experiment Directory')
        mainPath = dialog.getExistingDirectory(self, 'Select a directory')
        self.directoryW.txtZone.setText(mainPath)

        self.readConfigFile()

        with open("config.yaml", "w") as stream:
            try:
                print(self.config['Paths'])
                self.config['Paths']['MainPathExperiment'] = mainPath
                self.config = yaml.dump(self.config, stream)
            except yaml.YAMLError as exc:
                print(exc)

    def uiData(self, font):
        """
        define data output box with a video player for webcam recording
        :param font: QFont
        """
        self.BoxData = QGroupBox(self)
        self.BoxData.setFont(font)
        self.BoxData.setTitle("Data output")
        self.mainQGridLayout.addWidget(self.BoxData, 1, 1, 1, 1)

        self.gridBoxData = QHBoxLayout(self)
        self.BoxData.setLayout(self.gridBoxData)

        self.textBoxData = QTextEdit()
        self.textBoxData.setReadOnly(True)

        self.gridBoxData.addWidget(self.textBoxData)

        self.videoBox = VideoWidget()
        self.gridBoxData.addWidget(self.videoBox)

    def uiParam(self, font):
        """
        define parameter box
        :param font: QFont
        :return:
        """
        self.BoxParam = QGroupBox(self)
        self.BoxParam.setFont(font)
        self.BoxParam.setTitle("Measurement parameters")
        self.mainQGridLayout.addWidget(self.BoxParam, 0, 2, 1, 1)

        '''set Grid for Parameter Box'''''
        self.gridParam = QGridLayout(self)
        self.BoxParam.setLayout(self.gridParam)

        '''specify additional layout inside parameter layout'''
        self.paramNailQGridLayout = QGridLayout(self)
        self.paramDetectorQGridLayout = QGridLayout(self)
        self.paramCellQGridLayout = QGridLayout(self)
        self.paramNameQGridLayout = QGridLayout(self)

        '''add them to parameter layout'''
        self.gridParam.addLayout(self.paramNameQGridLayout, 0, 0, 1, 1)
        self.gridParam.addLayout(self.paramDetectorQGridLayout, 1, 0, 1, 1)
        self.gridParam.addLayout(self.paramNailQGridLayout, 2, 0, 1, 1)
        self.gridParam.addLayout(self.paramCellQGridLayout, 3, 0, 1, 1)

        '''General parameters > Name, time, date
        Loop through config file and create boxes according to existing entries'''
        self.configParameterGeneral = self.config['MeasurementParameters']['general']
        self.ParamGeneral = []
        for idx in range(len(self.configParameterGeneral)):
            self.paramNameQGridLayout.addWidget(QLabel(self.configParameterGeneral[idx] + ': '), 0, idx * 2, 1, 1)
            self.Box = self.textBox("-")  # TODO: get data from selected excel file
            self.paramNameQGridLayout.addWidget(self.Box, 0, idx * 2 + 1, 1, 1)
            self.ParamGeneral.append(self.Box)

        '''Detector specific parameters'''
        self.BoxDetector = QGroupBox(self)
        self.BoxDetector.setFont(font)
        self.BoxDetector.setTitle("Detector")
        self.paramDetectorQGridLayout.addWidget(self.BoxDetector, 0, 0)

        self.gridDetector = QGridLayout(self)
        self.BoxDetector.setLayout(self.gridDetector)

        self.configParameterDetector = self.config['MeasurementParameters']['Detector']
        self.ParamDetector = []

        for idx in range(len(self.configParameterDetector)):
            max_numCol = self.config['GUISettings']['MaxNumCol']
            row = math.floor(idx / max_numCol)
            idx_col = idx % max_numCol
            self.gridDetector.addWidget(QLabel(self.configParameterDetector[idx] + ': '), row, idx_col * 2, 1, 1)
            self.Box = self.textBox("-")
            self.gridDetector.addWidget(self.Box, row, idx_col * 2 + 1, 1, 1)
            self.ParamDetector.append(self.Box)

        '''Nail specific parameters'''
        self.BoxNail = QGroupBox(self)
        self.BoxNail.setFont(font)
        self.BoxNail.setTitle("Nail")
        self.paramNailQGridLayout.addWidget(self.BoxNail, 0, 0)

        self.gridNail = QGridLayout(self)
        self.BoxNail.setLayout(self.gridNail)

        self.configParameterNail = self.config['MeasurementParameters']['Nail']
        self.ParamNail = []

        for idx in range(len(self.configParameterNail)):
            max_numCol = self.config['GUISettings']['MaxNumCol']
            row = math.floor(idx / max_numCol)
            idx_col = idx % max_numCol
            self.gridNail.addWidget(QLabel(self.configParameterNail[idx] + ': '), row, idx_col * 2, 1, 1)
            self.Box = self.textBox("-")
            self.gridNail.addWidget(self.Box, row, idx_col * 2 + 1, 1, 1)
            self.ParamNail.append(self.Box)

        '''cell specific parameters'''
        self.BoxCell = QGroupBox(self)
        self.BoxCell.setFont(font)
        self.BoxCell.setTitle("Cell")
        self.paramCellQGridLayout.addWidget(self.BoxCell, 0, 0)

        self.gridCell = QGridLayout(self)
        self.BoxCell.setLayout(self.gridCell)

        self.configParameterCell = self.config['MeasurementParameters']['Cell']
        self.ParamCell = []

        for idx in range(len(self.configParameterCell)):
            max_numCol = self.config['GUISettings']['MaxNumCol']
            row = math.floor(idx / max_numCol)
            idx_col = idx % max_numCol
            self.gridCell.addWidget(QLabel(self.configParameterCell[idx] + ': '), row, idx_col * 2, 1, 1)
            self.Box = self.textBox("-")
            self.gridCell.addWidget(self.Box, row, idx_col * 2 + 1, 1, 1)
            self.ParamCell.append(self.Box)

    def locateData(self):
        """
        Method to locate all the different data in the current working directory
        IF the default data folder is not found use the excel file directory name
        """
        # TODO send error message if not all the data are presents
        # TODO widget to select which data to select'''

        self.nameMainFolder = str(self.ParamGeneral[0].text())
        self.readConfigFile()
        mainpath = self.config['Paths']['MainPathExperiment']

        path = mainpath + '/' + self.nameMainFolder
        for folder in os.listdir(path):
            if 'Xray' in folder:
                self.pathXray = os.path.join(mainpath, self.nameMainFolder, folder)


        path = os.path.join(mainpath,self.nameMainFolder, self.nameMainFolder + '_Video')
        print('***')
        print(glob.glob(path+'\*'))
        for folder in os.listdir(path):
            if '.mp4' in folder:
                self.pathVideo = os.path.join(mainpath, self.nameMainFolder, self.nameMainFolder + '_Video/', folder)


        self.pathRef = os.path.join(mainpath, self.nameMainFolder, self.nameMainFolder + '_Ref')
        self.pathTC = os.path.join(mainpath, self.nameMainFolder, self.nameMainFolder + '_TC')
        self.pathTranscom = os.path.join(mainpath, self.nameMainFolder,
                                         self.nameMainFolder + '_Transcom/' + self.nameMainFolder + '.tpc5')


        if 'PP' in self.nameMainFolder or 'SP' in self.nameMainFolder or 'NP' in self.nameMainFolder:
            self.flag_propagation = True
        else:
            self.flag_propagation = False

        if not os.path.isdir(self.pathXray):
            nameExcel = 'Filename Xray'
            for i, name in enumerate(self.headerNames):
                if name == nameExcel:
                    Xrayfoldername = self.dataM[i]
                    self.pathXray = os.path.join(mainpath, self.nameMainFolder, Xrayfoldername)

        if not os.path.isdir(self.pathRef):
            nameExcel = 'Filename Ref'
            for i, name in enumerate(self.headerNames):
                if name == nameExcel:
                    Reffoldername = self.dataM[i]
                    self.pathRef = os.path.join(mainpath, self.nameMainFolder, Reffoldername)

        if not os.path.isdir(self.pathTC):
            nameExcel = 'Filename TC'
            for i, name in enumerate(self.headerNames):
                if name == nameExcel:
                    TCfoldername = self.dataM[i]
                    self.pathTC = os.path.join(mainpath, self.nameMainFolder, TCfoldername)

        if not os.path.isfile(self.pathTranscom):
            nameExcel = 'Filename Transcom'
            for i, name in enumerate(self.headerNames):
                if name == nameExcel:
                    Transcomfoldername = self.dataM[i]
                    self.pathTranscom = os.path.join(mainpath, self.nameMainFolder, Transcomfoldername)

        if not os.path.isfile(self.pathVideo):
            nameExcel = 'Filename Video'
            for i, name in enumerate(self.headerNames):
                if name == nameExcel:
                    Videofoldername = self.dataM[i]
                    self.pathVideo = os.path.join(mainpath, self.nameMainFolder, Videofoldername)

    def bLoadClicked(self):
        """
        This function is executed when the "Import Data" button is pressed
        """
        self.newState('Importing data...')  # TODO write status msg
        dialog = ImportDialog()
        fileName = dialog.filename
        fileNameIdx = dialog.filenameIdx
        self.newState('Selected Measurement:' + fileName)

        '''get all parameter values of selected measurement from experimentalList'''
        [self.headerNames, self.dataM] = readXLSX.getMData('ExperimentalList.xlsx', fileNameIdx)

        '''update GUI with new parameters'''

        count = 0
        for count in range(0,20):
            if count <= 2:
                idxText = self.dataM[count]
                self.ParamGeneral[count].setText(str(idxText))

            elif count <= 7:
                idxText = self.dataM[count]
                self.ParamDetector[count-3].setText(str(idxText))

            elif count <= 10:

                idxText = self.dataM[count]
                self.ParamNail[count-8].setText(str(idxText))

            elif count <= 14:
                idxText = self.dataM[count]
                self.ParamCell[count-11].setText(str(idxText))
            print(count)

        '''    
            
            elif names in self.configParameterNail:
                idxName = (self.configParameterNail).index(names)
                idxText = self.dataM[count]
                self.ParamNail[names].setText(str(idxText))
                count = count + 1
            
                count = count + 1
            elif names in self.configParameterCell:
                idxName = (self.configParameterCell).index(names)
                idxText = self.dataM[count]
                self.ParamCell[names].setText(str(idxText))
                count = count + 1
        '''

        self.locateData()

        self.newState('Importing data from tpc5 file. Please wait ...')
        print(self.pathTranscom)
        self.tcp5loader = importTPC5(self.pathTranscom)
        self.listDataNames = self.tcp5loader.getDatasets()
        [self.TriggerSample, self.SamplingRate, self.nSamples] = self.tcp5loader.getParams()
        [self.chName, self.physicalUnit, self.data] = self.tcp5loader.getAllData()
        print(self.chName)
        print(np.array(self.data))
        dataTosave = {self.chName[5]:np.array(self.data[5][0:-1:100]),self.chName[6]:np.array(self.data[6][0:-1:100]),self.chName[7]:np.array(self.data[7][0:-1:100])}
        df = pd.DataFrame(dataTosave)
        df.to_csv('data.csv')
        #np.savetxt('test.txt',np.column_stack(self.data),'\t', fmt='%s')

        print(self.SamplingRate)

        ''' update dropdownmenu with the new names '''
        self._cbData.clear()
        self._cbData.addItems(self.listDataNames)
        self.newState('Measurement data is available!')

        '''Call signal from the first channel to avoid error from the visu after loading images'''
        self.cbDataIndexChanged(1)

        '''Look in the xls file for the frame rate of the X-ray images and TC image'''
        nameExcel = 'FPS Xray'
        for i, name in enumerate(self.headerNames):
            if name == nameExcel:
                self.Xray_fps = self.dataM[i]

        nameExcel = 'FPS TC'
        for i, name in enumerate(self.headerNames):
            if name == nameExcel:
                self.TC_fps = self.dataM[i]

        '''Set up the slider min and max value to match the transcom data signals'''
        max_slider = len(self.data[0]) - 1

        self.sliderData.slider.setMinimum(0)
        self.sliderData.slider.setMaximum(max_slider)

        self.xRayVisu.imageVisualizer.sliceSlider.slider.setMinimum(0)
        self.xRayVisu.imageVisualizer.sliceSlider.slider.setMaximum(max_slider)

        self.tempVisu.imageVisualizer.sliceSlider.slider.setMinimum(0)
        self.tempVisu.imageVisualizer.sliceSlider.slider.setMaximum(max_slider)

        '''Init the visualiser to the transcom data'''

        self.xRayVisu.imageVisualizer.sliceSlider.time_array = self.t
        self.tempVisu.imageVisualizer.sliceSlider.time_array = self.t
        self.sliderData.time_array = self.t

        '''Find the start of the x-ray and TC images from the two given trigger channels'''

        nameExcel = 'X-ray Camera Trigger Channel'
        for i, name in enumerate(self.headerNames):
            if name == nameExcel:
                Xray_channel = self.dataM[i]

        nameExcel = 'TC Camera Trigger Channel'
        for i, name in enumerate(self.headerNames):
            if name == nameExcel:
                TC_channel = self.dataM[i]

        nameExcel = 'Trigger X-ray Threshold'
        for i, name in enumerate(self.headerNames):
            if name == nameExcel:
                thXrayChannel = float(self.dataM[i])

        nameExcel = 'Trigger TC Threshold'
        for i, name in enumerate(self.headerNames):
            if name == nameExcel:
                thTCChannel = float(self.dataM[i])

        trigger_Xray_data = self.data[Xray_channel - 1]
        trigger_TC_data = self.data[TC_channel - 1]

        Xray_trigger_reader = readTrigger(trigger_Xray_data)
        TC_trigger_reader = readTrigger(trigger_TC_data)

        self.delay_Xray = Xray_trigger_reader.compute_trigger_delay(thXrayChannel)

        self.delay_TC = TC_trigger_reader.compute_trigger_delay(thTCChannel)

        '''Recompute the frame rate of both images  based on the # of images to skip '''
        self.frames_skip_xray = self.config['GUISettings']['Frames_skip_xray']
        self.frames_skip_TC = self.config['GUISettings']['Frames_skip_TC']

        self.Xray_fps_GUI = self.Xray_fps / self.frames_skip_xray
        self.TC_fps_GUI = self.TC_fps / self.frames_skip_TC

        ratio_Xray = self.SamplingRate / self.Xray_fps_GUI
        ratio_TC = self.SamplingRate / self.TC_fps_GUI

        self.xRayVisu.imageVisualizer.delay = self.delay_Xray
        self.tempVisu.imageVisualizer.delay = self.delay_TC

        self.xRayVisu.imageVisualizer.ratiofps = ratio_Xray
        self.tempVisu.imageVisualizer.ratiofps = ratio_TC

        '''Load Images for x-ray and temp'''
        self.newState('Loading X-ray images')
        xrayreader = XrayReader(self.pathXray, self.frames_skip_xray)
        xraydata = xrayreader.readAllImages()
        self.xRayVisu._setDataVolume(xraydata)
        number_xray_frames = self.xRayVisu.imageVisualizer.dataVolume.shape[0]
        self.delay_Xray = self.delay_Xray - ratio_Xray * number_xray_frames

        self.newState('Loading TC images')

        reader = tempTxtFileReader(self.pathTC, self.frames_skip_TC)
        tempdata = reader.readSeqImage()

        listaverageTC = []
        listframes = []

        for i, temp_slice in enumerate(tempdata):
            mean = np.mean(temp_slice)
            listaverageTC.append(mean)
            listframes.append(i)
        listaverageTC = np.array(listaverageTC)

        trigger_peak = np.where(listaverageTC == np.max(listaverageTC))[0][0]

        if self.flag_propagation:
            Tc_propagation = self.TC_fps_GUI * 60
            crop_signal = Tc_propagation + trigger_peak
            propagation_peak = np.where(listaverageTC == np.max(listaverageTC[int(crop_signal):]))[0][0]
            print('Propagation peak', propagation_peak)
            delay_TC = propagation_peak * self.TC_fps_GUI
            print('delay_TC', delay_TC)

            T_peak_P_channel = self.data[7]
            T_peak = np.where(T_peak_P_channel == np.max(T_peak_P_channel))[0][0]
            print(T_peak, self.SamplingRate)
            transcom_points = self.SamplingRate * T_peak
            print('transcom points', transcom_points)
            start_point = transcom_points - delay_TC
            delay_dispaly_TC = start_point / self.SamplingRate
            print('delay_display_TC', delay_dispaly_TC)

        else:
            delay_TC = self.TC_fps_GUI * trigger_peak
            T_peak_T_channel = self.data[6]
            T_peak = np.where(T_peak_T_channel == np.max(T_peak_T_channel))[0][0]
            transcom_points = self.SamplingRate * T_peak
            start_point = transcom_points - delay_TC
            delay_dispaly_TC = start_point / self.SamplingRate

        self.tempVisu.imageVisualizer.delay = delay_dispaly_TC

        self.tempVisu._setDataVolume(tempdata)

        '''Load mp4 files'''
        self.newState('Loading Webcam file')
        self.videoBox.openFile(self.pathVideo)

        ''''Analyse data '''
        self.newState('Analysing Data')

        analysis = signalAnalysis(self.data, self.chName, self.t)

        text_to_Display = ''
        text_to_Display += str(self.nameMainFolder) + ':\n'
        text_to_Display += '\n'
        text_to_Display += 'Max Temperature Cell 1: ' + str(round(analysis.maxTcell1, 3)) + ' °C\n'
        text_to_Display += 'Max Temperature Cell 2: ' + str(round(analysis.maxTcell2, 3)) + ' °C\n'
        text_to_Display += 'Max Temperature Chamber: ' + str(round(analysis.maxT_chamber, 3)) + ' °C\n'
        # text_to_Display += 'Time V drop Cell 1: ' + str(round(analysis.timeVdrop_cell1,3)) + ' s\n'
        # text_to_Display += 'Time V drop Cell 2: ' + str(round(analysis.timeVdrop_cell2,3)) + ' s\n'
        text_to_Display += '\n'

        # Get comments of xls to display in the results section
        nameExcel = 'Comments'
        for i, name in enumerate(self.headerNames):
            if nameExcel in name:
                comments = self.dataM[i]

        nameExcel = 'Propagation/No Propagation'
        for i, name in enumerate(self.headerNames):
            if nameExcel in name:
                propagation = self.dataM[i]

        text_to_Display += 'Propagation Status: ' + propagation + '\n'
        text_to_Display += 'Comments: ' + comments + '\n'

        font2 = QtGui.QFont('Times', 12)
        font2.setBold(True)
        font2.setWeight(75)
        self.textBoxData.setFont(font2)
        self.textBoxData.setText(text_to_Display)

        self._cbData.setEnabled(True)
        self._ButtonSave.setEnabled(True)


    def cbDataIndexChanged(self, index):
        """
        This function is executed when the a new entry in the Dropdownmenu is selected
        :param index: index of the drop down menu
        """
        self.indextranscom = index
        self.dataName = self.listDataNames[index]
        if index > 0:
            self.newState('Data: ' + self.dataName + ' will be display')

            tmp_data = self.data[index - 1]
            tmp_label = self.chName[index - 1]
            unit = '[ ' + self.physicalUnit[index - 1] + ' ]'

            TimeScale = 1
            startTime = -self.TriggerSample / self.SamplingRate * TimeScale
            endTime = (len(tmp_data) - self.TriggerSample) / self.SamplingRate * TimeScale
            self.t = np.arange(startTime, endTime, 1 / self.SamplingRate * TimeScale)

            self.figure.clf()
            self.ax3 = self.figure.add_subplot(111)
            self.ax3.plot(self.t, tmp_data, label=tmp_label)
            self.vLine = self.ax3.axvline(x=self.t[0], color="r")
            self.label = self.ax3.text(np.min(self.t), np.max(tmp_data) * 0.8)
            self.ax3.set_xlabel('Time')

            ''' Scale x Axis '''
            if TimeScale == 1:
                self.ax3.set_xlabel('time (s)')
            elif TimeScale == 1000:
                self.ax3.set_xlabel('time (ms)')
            elif TimeScale == 1000000:
                self.ax3.set_xlabel('time (us)')
            self.ax3.set_ylabel(unit)
            self.ax3.grid(True)

            self.canvas.draw_idle()


    def textBox(self, textInput):
        """
        function for easy creation of QLineEdit Widgets -> used for displaying the measurement parameters
        :param textInput: string to display in the various QLineEdit
        :return: QLineEdit
        """

        qText = QLineEdit(textInput, self)
        qText.setReadOnly(True)
        qText.setMaximumWidth(100)
        font = QtGui.QFont()
        font.setBold(False)
        qText.setFont(font)
        return qText


    def newState(self, message):
        """
        function for writing messages to the status Text field
        :param message: string message
        :return:
        """

        self._textBox.moveCursor(QtGui.QTextCursor.End)
        current = self._textBox.toPlainText()

        if current == self.init_text:
            self._textBox.setPlainText(message)
        else:
            self._textBox.insertPlainText("\n" + message)

        sb = self._textBox.verticalScrollBar()
        sb.setValue(sb.maximum())


    def closeEvent(self, event):
        """
        close event -> is executed if you press "X" in the main window
        :param event: QEvent
        :return:
        """

        reply = msgBox.question(self, 'Close request', 'Are you sure you want to close the window?', msgBox.Yes | msgBox.No,
                                msgBox.No)

        if reply == msgBox.Yes:
            event.accept()
        else:
            event.ignore()

        self.tcp5loader.closeFile()


class ImportDialog(QDialog):
    """
    new window with a list of all available measurements
    return value is used to get the id for the data to be imported in the main window
    """

    def __init__(self):
        super().__init__()
        self.title = 'Measurements'
        self.initUI()

    def initUI(self):
        self.buttonClicked = False
        self.filename = []
        self.setWindowTitle(self.title)

        self.importDialogQGridLayout = QGridLayout()

        self.ListWidget = QListWidget()

        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)

        self.ListBox = QGroupBox(self)
        self.ListBox.setFont(font)
        self.ListBox.setTitle("Available measurements")
        scroll_bar = QScrollBar(self)
        self.ListWidget.setVerticalScrollBar(scroll_bar)

        ButtonBox = QDialogButtonBox()
        self.ButtonImport = QPushButton("Import selected measurement", self)
        ButtonBox.addButton(self.ButtonImport, QDialogButtonBox.ActionRole)
        self.ButtonImport.clicked.connect(self.importButtonClicked)

        self.importDialogQGridLayout.addWidget(self.ListBox, 0, 0)
        self.importDialogQGridLayout.addWidget(self.ButtonImport, 1, 0)

        '''create vBox for data plot'''
        self.vboxList = QVBoxLayout(self)
        self.ListBox.setLayout(self.vboxList)

        self.vboxList.addWidget(self.ListWidget)

        self.openImportDialog()

        self.setLayout(self.importDialogQGridLayout)
        self.show()
        self.exec_()

    def openImportDialog(self):
        """
        import "param" values from all available measurement in experimental list
        """

        param = ["Date", "Time", "Name"]
        self.measurement_names = readXLSX.getMName('ExperimentalList.xlsx', param)

        self.ListWidget.clear
        self.ListWidget.addItems(self.measurement_names)

    def importButtonClicked(self):
        """
        Method called when the import button is clicked
        :return: string of the filename to import
        """

        if self.ListWidget.selectedItems() != []:
            self.buttonClicked = True
            self.close()
            self.filename = self.ListWidget.currentItem().text()
            self.filenameIdx = self.ListWidget.currentRow()
            return self.filename

    def closeEvent(self, event):
        """
        Method Called when the close button is called
        :param event: QEvent
        """
        noItemSelected = self.ListWidget.selectedItems() == []

        if self.buttonClicked == False:
            if noItemSelected == True:
                reply = msgBox.question(self, 'Close request', 'No Data selected. Still want to close?',
                                        msgBox.Yes | msgBox.No, msgBox.No)
            else:
                reply = msgBox.question(self, 'Close request', 'Data selected. Import selected data',
                                        msgBox.Yes | msgBox.No, msgBox.No)
            if (reply == msgBox.Yes) and noItemSelected:
                event.accept()
                self.filename = []
                return self.filename
            elif (reply == msgBox.Yes) and (noItemSelected == False):
                self.filename = self.ListWidget.currentItem().text()
                self.filenameIdx = self.ListWidget.currentRow()
                return self.filename
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    state_window = MainWindow()
    app.exec()
