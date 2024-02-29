# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 13:38:08 2022

@author: PfaffJ
"""

import pandas as pd
import datetime

class readXLSX():
    
    def getMData(path, idxMeasurement = 1):
        # Select ile 
        # infile = path
        infile = 'ExperimentalList.xlsx'
        # Use skiprows to choose starting point and nrows to choose number of rows
        
        data = pd.read_excel(infile)
        
        listHeader = list(data.columns)
        

        
        dataList = []
        for idx in listHeader:
            dataList.append(data[idx].iloc[idxMeasurement])
            # print(data[idx].iloc[idxMeasurement])
        
        return listHeader, dataList
    
    def getMName(path,param):
        # Select file 
        infile = path
        # infile = 'ExperimentalList.xlsx'
        # Use skiprows to choose starting point and nrows to choose number of rows
        
        data = pd.read_excel(infile)
        
        len_data = len(data)
        
        numParam = len(param)
        
        listHeader = list(data.columns)
        
        for nameParam in param:
            try:
                tmp_data = data.loc[:,nameParam]
                # idx = listHeader.index(nameParam)
                # print(idx)
            except:
                print(nameParam + "Name was not in List") #TODO
        tmp_data = data.loc[:,param]
        tmp_list = tmp_data.values.tolist()
        listNames = []
        for idx in range(0,len_data):
            count = 0
            for element in tmp_list[idx]:
                list_new = tmp_list[idx]
                if isinstance(element, datetime.time):
                    tmp_string = element.strftime("%H:%M:%S")
                    # print(tmp_string)
                    # index = list_new[idx].index(element)
                    list_new[count] = tmp_string
                count = count + 1
            listNames.append(' - '.join(list_new))
                                
        
        return listNames


if __name__ == '__main__':
    test_xls = readXLSX()
    print(test_xls.getMData(0))