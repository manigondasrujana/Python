import pandas as pd
import numpy as np
import re
import datetime as dt
import os

#import the excel file as a dataframe
products = pd.read_excel("data_wrangling_homework-2.xlsx",index=False)

#extract the product names as a list
rowlist = products['Unnamed: 0'].tolist()

#drop the product names from the dataframe
products.drop(['Unnamed: 0'],axis=1,inplace=True)

#products.set_index([rowlist], inplace = True)

#Function to count number of prefix underscores in a string
def uscounter(string):
    uslen = 0
    for x in string:
        if x == '_':
            uslen += 1
        else:
            break
    return uslen

#finalrows will store the final joined item names.
finalrows = []

#accumulater will store intermediate names during the for loop and append it to the final rows
accumulater = []

#head will store the product category of the items 'A','B' and 'C'. Initialized it to empty string
head = ''

#prev_len will store the number of underscores in the previous string. This is used to check item levels
prev_len = 0

#iterate through the product name
for x in range(0,len(rowlist)):
    #count the number of _ in current string
    _count = uscounter(rowlist[x])
    
    #when the current string is the product category of the items 'A','B' and 'C'.
    if _count == 0:
        
        #update the product category name
        head = rowlist[x]
        
        #if its the first time Encountering a product category,no need to append
        #the empty accumulater to the finalrows.
        if x == 0:
            accumulater.append(rowlist[x])
        
        #else append the accumulater items to the final rows and empty it.
        #Then add the head(product category) to the accumulater and update
        #the previous underscore count to 0.
        else:
            finalrows.append(accumulater)
            accumulater = []
            accumulater.append(head)
            prev_len = 0
            
    #if the current string is not a category, compare the previous underscore counts
    #to the current count to check if the current string should be added to the accumulater.
    else:
        #if current count is greater than previous count, current element will be added to
        #the accumulater and previous count is updated to current count.
        if _count>prev_len:
            accumulater.append(rowlist[x])
            prev_len = _count
        
        #if current count is less than previous count, it means that this is a new item.
        #append the accumulater to the finalrows, and empty it.
        #Then add the current head (product category) and current element to it.
        #previous count is updated to current count.
        elif _count<prev_len:
            finalrows.append(accumulater)
            accumulater = []
            accumulater.append(head)
            accumulater.append(rowlist[x])
            prev_len = _count
        
        #if current count is equal to previous count, it means that this item is from the same level
        #as the previous item. append the accumulater to the final rows. Remove the last element from
        #the accumulater and append the current element to it. Update the previous count.
        else:
            finalrows.append(accumulater)
            accumulater = accumulater[:-1]
            accumulater.append(rowlist[x])
            prev_len = _count

#After this loop we have the last accumulater contents still left, so we add it to the final rows.
finalrows.append(accumulater)

#join all the names for each item.
for x in range(0,len(finalrows)):
    finalrows[x] = ''.join(finalrows[x])

#Clean all the joined item names for the extra underscores using regex.
#The cleaned finalrows for the current input data is:
#['A_white_ivory_tan_egg', 'A_white_ivory_tan_apple', 'A_red_pink_apple', 'B_purple_navy_tan_banana',
#'B_red_pink_banana', 'B_blue_red_orange_apple', 'B_ivory_pink_banana', 'C_blue_ivory_pink_egg']
for x in range(0,len(finalrows)):
    finalrows[x] = re.sub('\_+', '_', finalrows[x]).strip('_')

#change datetime column to just date.
products.columns = pd.to_datetime(products.columns).date

#level 1 for the multindexed columns
level_one = []

#duplicate it two times since each column will have 2 sub columns (index, number)
for i in finalrows:
    level_one.extend([i, i])

#level 2 for the multindexed columns. duplicate it as the same number as the number of columns.
level_two = ['Index','Number'] * len(finalrows)

#initialize multilevel index
multilevel = [level_one,level_two]

#change it to a tuple
tuples = list(zip(*multilevel))

#set the multiindex for the columns 
index = pd.MultiIndex.from_tuples(tuples)

#drop the NaN values from the dataframe
products = products.dropna()

#reset all the indexs from the dataframe
products.reset_index(drop=True, inplace = True)

#store the dates in a numpy array
dates = products.columns.get_values()

#ssd is a new dataframe which has the dates as columns
ssd = pd.DataFrame(dates)

#add the same dates columns as the number of finalrows
for x in range(1,len(finalrows)):
    ssd[x] = ssd[0]

#transpose it to rows
ssd = ssd.T

#set the column index as the first row
ssd.columns = ssd.iloc[0]

#now merge the product dataframe and the ssd dataframe. This will give us the combined dataframe
#with alternate rows from each data frame
products = pd.concat([ssd, products]).sort_index(kind='merge')

#set the multindex we built earlier to the products dataframe
products = products.set_index(index)

#transpose it to get the desired format
products = products.T

#reset the indexing
products.reset_index(drop = True, inplace = True)

#get the current working directory
currentdir = os.getcwd()

#create a folder in the current directory path to store the output csv files
path = currentdir + '/output_files'

#create the output folder 
os.mkdir(path)

#for each column in the multindexed dataframe, output the column in a new csv file
#in the ouput folder with the item name as the filename
for x in finalrows:
    products[x].to_csv('output_files/{}.csv'.format(x), index = False)
    
#The final dataframe from which I am creating the files(from its columns).
products