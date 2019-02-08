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
        output['SOC Code'] = output['SOC Code'].apply(lambda row: row[2:9])
        
    return output

#read in the god awful xls table made by national center for education statistics
    #same as before, pass online=True if it should be called in the ipynb
def read_nces_xls(fileName, online = False):
    if online:
        githubBaseUrl = 'https://raw.githubusercontent.com/Crumbletheundead/Cogs9Project/master/'
        fullPath = githubBaseUrl + fileName
    else:
        fileDirPath = os.path.dirname(os.path.realpath(__file__))
        fullPath = os.path.join(fileDirPath, fileName)
    
    output = pd.read_excel(fullPath)
    
    #only take the column showing year and the column showing 
    #average tuition every year for 4 year institutions
        #tuition is adjusted for inflation rate to reflect value during 2016-2017 school year
    output = output[[output.columns[0], output.columns[1]]]
    output.columns = ['Year', 'Avg $ Tuition in 2016-17 $']
    
    #drop all the useless rows full of white spaces and messy labels
    #should only leave us with data from years 2006-2007 to 2016-2017
    output.drop(
                list(range(67,output['Year'].size)),
                inplace = True
                )
    output.drop(
                list(range(0,54)),
                inplace = True
                )
    output.dropna(inplace = True)
    
    #cut the year string so that they are the year that school year ends on
    #we use the one the school year ends on because that's when you'll start working
    #hence when you start having to pay your debts
    output['Year'] = output['Year'].apply(lambda string: '20'+string[5:7])
    
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
    output= master.merge(join, on= 'SOC Code')
    output = output.assign(Year = joinYear)
    
    return output

#uses aformentioned functions to read everything from directory
#and returns everything in a single dataframe
    #set online to true if running on class ipynb
def gather_ten(ipynb = False):
    checkBachelor = csv_to_table('EmploymentProjections.csv', bachelorSource = True, online = ipynb) 
    allYears = []
    
    #creates a dataframe for every single year's data and appends it into allYears list
    for i in range(11):
        print(i)
        allYears.append(merge_master_year(
                            checkBachelor, 
                            csv_to_table((str(2017-i) + '.csv'), online = ipynb), 
                            str(2017-i)
                        ))
    
    #smash everything together within allYears to make one giant table
    output = pd.concat(allYears)
    
    #call the tuition data and merge it into the master table
    tuition = read_nces_xls('tuitionData.xls', ipynb)
    output = output.merge(tuition, on = 'Year')
    
    #cast every dtype into actual integers so it'll be easier to work with
    output['Year'] = output['Year'].apply(lambda year: int(year))
    output['Median Income'] = output['Median Income'].apply(lambda income: tryInt(income))
    
    #Sorts by soc code then the year 
        #null values were entered as # in the original data, changed it to None 
            #only the 2007 CEO median income was # anyways
    output = output.sort_values(['SOC Code', 'Year'])
    output.reset_index(drop = True, inplace = True)
    output['Median Income'] = output['Median Income'].apply(lambda row: 'None' if row == '#' else row)
    
    return output

#tries to cast input into an int, python doesn't let me lambda try catches :(
def tryInt(incomes):
    try:
        return int(incomes)
    except:
        return incomes
    
#exports dataframe as csv
def csvpls(df):
    fileDirPath = os.path.dirname(os.path.realpath(__file__))
    fullPath = os.path.join(fileDirPath, 'Cogs9FullDataset.csv')
    df.to_csv(fullPath, encoding='utf-8')