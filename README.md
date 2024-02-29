To facilitate radiography post-data processing, and also allow fast evaluation of the results during the experiments, 
a data synchronization graphical user interface (GUI) has been developed specifically for the operation of the test environment 
presented in this study: https://doi.org/10.1107/s1600577522010244. This script imports all collected data, including radiography, 
thermal imaging, temperature/voltage data and nail penetration data and gives the user the ability to easily visualize all 
measurement parameters synchronized in time. Through this visualization, an initial interpretation from the time-synchronized 
data is thus possible after each experiment. This enables a progressive adaptation of the measurement matrix during the beamtime.

In the configuration file (.yaml), please define:

- GUI Settings:
    - Frames_skip_TC: Give a value of the ratio of the thermal imaging frames
      you wish to visualize. If the value = 100, every 100th frame will be
      imported to the GUI.
    - Frames_skip_xray: Give a value of the ratio of the Xray frames frames
      you wish to visualize. If the value = 1000, every 1000th frame will be
      imported to the GUI.
      
-Paths: 
    - ExperimentalList: An exelfile containing the name of all the experiments, followed by
      information such as magnification, pixel size, frame rate nessecary to run the GUI. 
    - MainPathExperiment: path to the main folder whwre all the experiement folders are
    - MeasurementParentFolder: Linkes the data saving structures, in this case for one


      ![image](https://github.com/matildafransson/RadiographyGUI/assets/97672734/32e73c20-b660-4821-a5ce-42a5dfbc4086)

      
      
