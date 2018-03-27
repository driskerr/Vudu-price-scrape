# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 09:21:44 2018

@author: kerrydriscoll
"""
import pandas as pd
from pandas import ExcelWriter
from openpyxl import load_workbook
import re
from time import time, sleep
import datetime
import random
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


"""
Measure Runtime to Evaluate Code Performance
"""
start_time = time()

"""
Open Web Browser
"""
option = webdriver.ChromeOptions()
option.add_argument(" — incognito")
browser = webdriver.Chrome(executable_path='/Users/kerrydriscoll/Downloads/chromedriver', chrome_options=option)

"""
Create DataFrame to Populate
"""
df_final = pd.DataFrame(columns=['Vudu ID', 'Title', 'Rent SD','Rent HD','Own SD','Own HD', 'Time Stamp'])

"""
Input MOVIE IDs to reach URL
"""

#Just the Exercise Titles
#IDs=[835625, 763662, 743740, 525129, 873206, 651466]

#All A24 Titles
#IDs=[906857,835625,651466,763662,908845,743740,449248,873206,767196,682856,648015,464733,922802,465463,629676,841184,777616,761091,569326,682864,532860,906851,857020,904978,613624,859637,892541,875682,548125,569937,613628,577582,449252,525129,854035,820936,752289,802860,656520,682769,772893,778798,701080,772897,554166,400352,910082,770860,772913,841181,752293,805744,772889,732396,914602,656524,829645]
IDs=pd.read_excel('/Users/kerrydriscoll/Desktop/resumes/A24/A24 IDs.xlsx')['VUDU'].tolist()

try_again = []

"""
Extract Data for each MOVIE
"""
for ID in IDs:
    browser.get("https://www.vudu.com/content/movies/details/title/{}".format(ID))

    # Wait 20 seconds for page to load
    timeout = 20
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//h1[@class='head-big _3ehdP']")))
    except TimeoutException:
        print("Timed out waiting for page to load")
        browser.quit()
        
    """
    Extract Movie Title
    """

    title_element = browser.find_elements_by_xpath("//h1[@class='head-big _3ehdP']")
    title = [x.text for x in title_element]
    
    """
    Extract SD Rent & Own Prices
    """

    price_element = browser.find_elements_by_xpath("//div[@class='row nr-p-0 nr-mb-10']")
    prices = [x.text for x in price_element]

    rent_SD = re.search('Rent \$(\d*\.?\d*)', prices[0]).group(1)
    own_SD = re.search('Own \$(\d*\.?\d*)', prices[0]).group(1)
    
    """
    Extract HD Rent Price
    """
    sleep(random.uniform(0.3, 0.8))
    
    #Hover Mouse over Rents to Reveal Definition Options
    rent_element_to_hover_over_xpath = browser.find_elements_by_xpath("//div[@class='col-xs-4 nr-p-0']")
    rent_element_to_hover_over = rent_element_to_hover_over_xpath[0]
    rent_hover = ActionChains(browser).move_to_element(rent_element_to_hover_over)
    rent_hover.perform()
    
    # Wait for page to load
    #sleep(randint(18,30))
    timeout = 5
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='_29bQb']")))
    except TimeoutException:
        print("Timed out waiting for page to load, rental, {}".format(title[0]))
        try_again.append(ID)
        continue

    # Pull HD rental price
    rent_price_deatil_element = browser.find_elements_by_xpath("//div[@class='_29bQb']")            
    rent_prices_deatil = [x.text for x in rent_price_deatil_element]
    rent_HD = re.search('HDX \$(\d*\.?\d*)',rent_prices_deatil[0]).group(1)

    """
    Extract HD Own Price
    """
    #Hover Mouse over Own to Reveal Definition Options  
    own_element_to_hover_over_xpath = browser.find_elements_by_xpath("//div[@class='col-xs-4 nr-pl-10 nr-pr-0']")
    own_element_to_hover_over = own_element_to_hover_over_xpath[0]
    own_hover = ActionChains(browser).move_to_element(own_element_to_hover_over)
    own_hover.perform()
    
    # Wait for page to load
    #sleep(randint(18,30))
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='_29bQb']")))
    except TimeoutException:
        print("Timed out waiting for page to load, own, {}".format(title[0]))
        try_again.append(ID)
        continue
        
    # Pull HD purchase price
    own_price_deatil_element = browser.find_elements_by_xpath("//div[@class='_29bQb']")
    own_prices_deatil = [x.text for x in own_price_deatil_element]
    own_HD = re.search('HDX \$(\d*\.?\d*)',own_prices_deatil[0]).group(1)
    
    """
    Combine with other Titles
    """

    df = pd.DataFrame({'Vudu ID': ID, 'Title': title[0], 'Rent SD': [rent_SD],'Own SD':[own_SD], 'Rent HD':[rent_HD], 'Own HD':[own_HD], 'Time Stamp':datetime.datetime.now().strftime("%H:%M:%S")})
    df = df[['Vudu ID', 'Title', 'Rent SD','Rent HD','Own SD','Own HD', 'Time Stamp']]

    df_final = df_final.append(df, ignore_index=True)


df_final['Vudu ID']=df_final['Vudu ID'].astype(int)
df_final.sort_values('Vudu ID', ascending=False, inplace=True)
df_final.set_index('Vudu ID', inplace=True)
df_final[['Rent SD', 'Rent HD', 'Own SD','Own HD']]=df_final[['Rent SD', 'Rent HD', 'Own SD','Own HD']].astype(float)
print(df_final)

browser.quit()

#if you want to change to currency format
#test = df_final
#test[['Rent SD', 'Rent HD', 'Own SD','Own HD']] = test[['Rent SD', 'Rent HD', 'Own SD','Own HD']].applymap("${0:.2f}".format)

#"""
path = '/Users/kerrydriscoll/Desktop/resumes/A24/vudu_prices.xlsx'
book = load_workbook(path)
writer = ExcelWriter(path, engine = 'openpyxl')
writer.book = book
df_final.to_excel(writer, sheet_name=datetime.date.today().strftime("%Y-%m-%d"))
#test.to_excel(writer)
writer.save()
#"""


run_time=time() - start_time
print("--- {} seconds ---".format(run_time))
print("--- {} seconds per title ---".format(run_time/len(df_final)))