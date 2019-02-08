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
        #SOC stands for standardized occupational codes used by bureau of labor stats
            #god bless bureacracies, saved me from writing another function just to merge data from different years
    if bachelorSource:
        output = output[['Occupation Title', 'SOC Code', 'Typical entry-level education']]
        output = output.rename(columns = {'Typical entry-level education': 'Typical Education Required'})
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
    output = output[[output.columns[0], output.columns[2]]]
    output.columns = ['Year', 'Avg Tuition']
    
    #drop all the useless rows full of white spaces and messy labels
        #I almost cried when I saw the xls data in a pandas dataframe
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
    #hence you won't need to pay next year's tuition
        #this is still only like a third of what I pay as an international student ;_;
    output['Year'] = output['Year'].apply(lambda string: '20'+string[5:7])
    
    return output
    
#creates a dataframe for any given year's data
#by joining it innerly against the bachelor source SOC codes
#This way only jobs that only require bachelor degrees show up, whilst all other jobs are dropped
#this way also drops some odd calculations present in the bachelor source
    #joinYear is the year of 'join' parameter dataframe
def merge_master_year(master, join, joinYear):

    #since some years have different labels, renames columns so that they may be joined
    #also drops the unnecessary columns from csvs for 'join' parameter
      #what witchery made them decide to capitalize their column labels starting 2010? no clue 
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

#uses aformentioned functions to read everything from directory or from my github page
#and returns everything in a single dataframe, so we don't have to jump around 12 different tables constantly
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
    #this way I can create a year column instead of having a column for every year's median income
      #see I did the reading and went to lecture 
      #if you're curious what the crappy table looked like check out our previous submission
    output = pd.concat(allYears)
    
    #call the tuition data and merge it into the master table
    tuition = read_nces_xls('tuitionData.xls', ipynb)
    output = output.merge(tuition, on = 'Year')
    
    #cast every dtype into actual integers so it'll be easier to work with
      #does this count as erasing tech debt
    output['Year'] = output['Year'].apply(lambda year: int(year))
    output['Median Income'] = output['Median Income'].apply(tryInt)
    
    #Sorts by soc code then the year
        #null values were entered as # in the original data, changed it to None 
            #only the 2007 CEO median income was # anyways
    #this is all simply for the aesthetics honestly, data is already workable before this step
      #but this way if you open it up in spyder it just looks so much better
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