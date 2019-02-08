# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 00:29:52 2019

@author: JeffWang
"""

import pandas as pd
import os

#load csv file in
#set bachelorSource = True if csv loaded is EmploymentProjections.csv
#set online to true if running on the class ipynb, god I love github they make life so easy
def csv_to_table(fileName, bachelorSource = False, online = False):
    output = None
    
    
    if online:
        githubBaseUrl = 'https://raw.githubusercontent.com/Crumbletheundead/Cogs9Project/master/'
        fullPath = githubBaseUrl + fileName
    else:
        fileDirPath = os.path.dirname(os.path.realpath(__file__))
        fullPath = os.path.join(fileDirPath, fileName)
    
    output = pd.read_csv(fullPath)
    
    #drops the unnecessary columns from EmploymentProjections.csv and formates SOC code
    if bachelorSource:
        output = output[['Occupation Title', 'SOC Code', 'Typical entry-level education']]
        output['SOC Code'] = output.apply(lambda row: row['SOC Code'][2:9], axis = 1)
        
    return output

#creates a dataframe for any given year's data
#by joining it against the bachelor source SOC codes
    #joinYear is the year of 'join' parameter dataframe
def merge_master_year(master, join, joinYear):

    #since some years have different labels, renames columns so that they may be joined
    #also drops the unnecessary columns from csvs for 'join' parameter
    if int(joinYear) >=2010:
        join = join[['OCC_CODE', 'A_MEDIAN']]
        join.columns = ['SOC Code', 'Median Income']

    else:
        join = join[['occ_code', 'a_median']]
        join.columns = ['SOC Code', 'Median Income']
        
    #joins the columns after column renaming
    output=  master.merge(join, how = 'inner', on= 'SOC Code')
    output['Year'] = joinYear
    return output

#uses aformentioned functions to read everything from directory
#and returns everything in a single dataframe
    #set online to true if running on class ipynb
def gather_ten(ipynb = False):
    master = csv_to_table('EmploymentProjections.csv', bachelorSource = True, online = ipynb) 
    allYears = []
    
    #creates a dataframe for every single year's data and appends it into allYears list
    for i in range(11):
        print(i)
        allYears.append(merge_master_year(
                            master, 
                            csv_to_table((str(2017-i) + '.csv')), 
                            str(2017-i)
                        ))
    
    #smash everything together within allYears
        #Sorts by soc code then the year 
        #null values were entered as # in the original data, changed it to None 
            #only the 2007 CEO median income was # anyways
    output = pd.concat(allYears)
    output = output.sort_values(['SOC Code', 'Year'])
    output.reset_index(drop = True, inplace = True)
    output['Median Income'] = output['Median Income'].apply(lambda row: 'None' if row == '#' else row)
    return output

#exports dataframe as csv
def csvpls(df):
    fileDirPath = os.path.dirname(os.path.realpath(__file__))
    fullPath = os.path.join(fileDirPath, 'Cogs9FullDataset.csv')
    df.to_csv(fullPath, encoding='utf-8')