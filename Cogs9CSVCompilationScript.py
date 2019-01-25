# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 00:29:52 2019

@author: JeffW
"""

import pandas as pd
import os
#sys.path.append("D:\Cogs9\Cogs9Project")

def csv_to_table(fileName, bachelorSource = False):
    output = None
    
    fileDirPath = os.path.dirname(os.path.realpath(__file__))
    fullPath = os.path.join(fileDirPath, fileName)
    
    output = pd.read_csv(fullPath)
    
    if bachelorSource:
        output = output[['Occupation Title', 'SOC Code', 'Typical entry-level education']]
        output['SOC Code'] = output.apply(lambda row: row['SOC Code'][2:9], axis = 1)
    else:
        output = output[['OCC_CODE', 'OCC_TITLE', 'OCC_GROUP', 'A_MEDIAN']]
        output.columns = ['SOC Code', 'OCC_TITLE', 'OCC_GROUP', 'A_MEDIAN']
        
    return output

def merge_master_year(master, join, joinYear):
    output=  master.merge(join, how = 'inner', on= 'SOC Code',)
    output = output.rename(columns = {'A_MEDIAN': joinYear+'_median_income'})
    return output