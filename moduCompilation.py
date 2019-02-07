# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 00:29:52 2019

@author: JeffW
"""

import pandas as pd
import os
#sys.path.append("D:\Cogs9\Cogs9Project")

#load csv file in
#set bachelorSource = True if csv loaded is EmploymentProjections.csv
def csv_to_table(fileName, bachelorSource = False):
    output = None

    fileDirPath = os.path.dirname(os.path.realpath(__file__))
    fullPath = os.path.join(fileDirPath, fileName)
    
    output = pd.read_csv(fullPath)
    
    if bachelorSource:
        output = output[['Occupation Title', 'SOC Code', 'Typical entry-level education']]
        output['SOC Code'] = output.apply(lambda row: row['SOC Code'][2:9], axis = 1)
        
    return output

def merge_master_year(master, join, joinYear):

    if int(joinYear) >=2010:
        join = join[['OCC_CODE', 'A_MEDIAN']]
        join.columns = ['SOC Code', 'A_MEDIAN']

    else:
        join = join[['occ_code', 'a_median']]
        join.columns = ['SOC Code', 'A_MEDIAN']
    output=  master.merge(join, how = 'inner', on= 'SOC Code',)
    output = output.rename(columns = {'A_MEDIAN': joinYear+'_median_income'})
    return output

def gather_ten():
    output = csv_to_table('EmploymentProjections.csv', bachelorSource = True)

    for i in range(11):
        print(i)
        output = merge_master_year(output, csv_to_table((str(2017-i) + '.csv')), str(2017-i))
    
    return output

def csvpls(df):
    fileDirPath = os.path.dirname(os.path.realpath(__file__))
    fullPath = os.path.join(fileDirPath, 'Cogs9FullDataset.csv')
    df.to_csv(fullPath, encoding='utf-8')