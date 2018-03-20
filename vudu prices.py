# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 09:21:44 2018

@author: kerrydriscoll
"""
import pandas as pd
from pandas import ExcelWriter
import re
from time import time, sleep
from random import randint
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
df_final = pd.DataFrame(columns=['Vudu ID', 'Title', 'Rent SD', 'Own SD', 'Rent HD', 'Own HD'])

"""
Input MOVIE IDs to reach URL
"""
IDs=[835625, 763662, 743740, 525129, 873206, 651466]


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
    
    #Hover Mouse over Rents to Reveal Definition Options
    rent_element_to_hover_over_xpath = browser.find_elements_by_xpath("//div[@class='col-xs-4 nr-p-0']")
    rent_element_to_hover_over = rent_element_to_hover_over_xpath[0]
    rent_hover = ActionChains(browser).move_to_element(rent_element_to_hover_over)
    rent_hover.perform()
    
    # Wait for page to load
    sleep(randint(15,25))

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
    sleep(randint(15,25))
        
    # Pull HD purchase price
    own_price_deatil_element = browser.find_elements_by_xpath("//div[@class='_29bQb']")
    own_prices_deatil = [x.text for x in own_price_deatil_element]
    own_HD = re.search('HDX \$(\d*\.?\d*)',own_prices_deatil[0]).group(1)
    
    """
    Combine with other Titles
    """

    df = pd.DataFrame({'Vudu ID': ID, 'Title': title[0], 'Rent SD': [rent_SD],'Own SD':[own_SD], 'Rent HD':[rent_HD], 'Own HD':[own_HD]})
    df = df[['Vudu ID', 'Title', 'Rent SD', 'Own SD', 'Rent HD', 'Own HD']]

    df_final = df_final.append(df, ignore_index=True)

df_final['Vudu ID']=df_final['Vudu ID'].astype(int)
print(df_final)


"""
writer = ExcelWriter('/Users/kerrydriscoll/Desktop/resumes/vudu_prices.xlsx')
df_final.to_excel(writer)
writer.save()
"""

run_time=time() - start_time
print("--- {} seconds ---".format(run_time))