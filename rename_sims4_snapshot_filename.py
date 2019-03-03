# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
import re
import datetime



def addzero(matchobj):
    return  '_0' + matchobj.group(0)[1:]

def add12_PM(matchobj):
    # get number
    number = int(re.sub('\D','',matchobj.group(0)))
    if number <= 12:
        number += 12
    # add 12
    return '_'+str(number) + '-'

def handle12_AM(matchobj):
    # get number
    number = int(re.sub('\D','',matchobj.group(0)))
    if number == 12:
        number = '00'
    # add 12
    return '_'+str(number) + '-'   


path="C:\\Users\\admin\\Documents\\Electronic Arts\\The Sims 4\\Screenshots"


main_path = 'E:\\sims4_screenshots_archive\\Jimmy'


#for sub_folder in os.listdir(main_path):
#    if '.' not in sub_folder:
#        path = os.path.join(main_path,sub_folder)
        
list_files = os.listdir(path)

for filename in list_files: 
    if re.match('\d{2}-\d{2}-\d{2}_\d{1,2}-\d{2}-\d{2}.*\.png',list_files[0]) is not None:
    
        test_str = filename 
        
        if 'PM' in test_str:
            test_str1 = re.sub('_\d{1,2}-', add12_PM, test_str)
        elif 'AM' in test_str:
            test_str1 = re.sub('_\d{1,2}-', handle12_AM, test_str)
        else:
            print("------------ BUG ------------- " + test_str)   
        
        test_str2 = re.sub('_\d{1}-', addzero, test_str1)   
        
        test_str3 = re.sub('^\d{2}-\d{2}-\d{2}', lambda x:datetime.datetime.strptime(x.group(0), "%m-%d-%y").strftime("%Y-%m-%d"), test_str2)
        print(os.path.join(path,test_str) + " --> " + test_str3)

        os.rename(os.path.join(path, filename), os.path.join(path, test_str3))

        
