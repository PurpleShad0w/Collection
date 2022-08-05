import os
import sys
import time
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scroll_to_bottom(driver):
    SCROLL_PAUSE_TIME = 7.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


user = 'PurpleShadow'

df = pd.DataFrame(data={'Title':0,'Platforms':0,'Hours Played':0,'Achievements Obtained':0,'Achievements Total':0,'Completion Percentage':0,'Last Played':0},index=(0,1))

# Load page
driver = webdriver.Chrome()
driver.get("https://www.exophase.com/user/"+user+"/")

# Deal with cookies popup
time.sleep(4)
iframe = driver.find_element(By.ID,"sp_message_iframe_681693")
WebDriverWait(driver,10).until(EC.frame_to_be_available_and_switch_to_it(iframe))
cookieButton = driver.find_element(By.XPATH,'//*[@id="notice"]/div[3]/button[3]')
WebDriverWait(driver,10).until(EC.element_to_be_clickable(cookieButton)).click()

# Sort game list
sortButton = driver.find_element(By.XPATH,'//*[@id="dropdownMenuButton"]')
sortButton.click()
alphaButton = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[1]/div[2]/div/div/a[7]')
alphaButton.click()
time.sleep(4)

scroll_to_bottom(driver)

# total_games = int(float(driver.find_element(By.XPATH,'//*[@id="sub-user-info"]/section[1]/div[3]/div/div[3]/div/div/span[4]').text))
i = 0

while True:
    try:
        title_xpath = '//*[@id="app"]/div/div[2]/div[1]/ul/li['+str(i+1)+']/div[1]/div[2]/div/h3/a'
        title_xpath_alt = '//*[@id="app"]/div/div[2]/div[1]/ul/li['+str(i+1)+']/div[1]/div[2]/div/h3'
        platform_xpath = '//*[@id="app"]/div/div[2]/div[1]/ul/li['+str(i+1)+']/div[1]/div[2]/div/div'
        hours_xpath = '//*[@id="app"]/div/div[2]/div[1]/ul/li['+str(i+1)+']/div[1]/div[2]/div/span'
        achiev_xpath = '//*[@id="app"]/div/div[2]/div[1]/ul/li['+str(i+1)+']/div[1]/div[4]/div[1]/div[1]'
        date_xpath = '//*[@id="app"]/div/div[2]/div[1]/ul/li['+str(i+1)+']/div[1]/div[5]/div'
        try:
            title = driver.find_element(By.XPATH,title_xpath).text
        except:
            title = driver.find_element(By.XPATH,title_xpath_alt).text
        try:
            hours = driver.find_element(By.XPATH,hours_xpath).text
        except:
            hours = '0h'
        try:
            achievements = driver.find_element(By.XPATH,achiev_xpath).text
        except:
            achievements = '0/0'
        try:
            date = driver.find_element(By.XPATH,date_xpath).text
        except:
            date = 'N/A'
    
        # Collect platforms
        j = 0
        platforms = []
        while True:
            j += 1
            try:
                platform = driver.find_element(By.XPATH,platform_xpath+'/div['+str(j)+']/span').text
                platforms.append(platform)
            except:
                break
    
        # Cleaning
        hours = hours[:-1]
        achiev_obtained, achiev_total = achievements.split('/')
        date = date.replace(',','')
        platforms = sorted(platforms)
        platforms = ' | '.join(platforms)
    
        # Append to dataframe
        s = pd.Series({'Title':title,'Platforms':platforms,'Hours Played':hours,'Achievements Obtained':achiev_obtained,'Achievements Total':achiev_total,'Completion Percentage':0,'Last Played':date})
        df = df.append(s,ignore_index=True)
        i += 1
    
    except:
        break

# Cleaning
df = df.drop_duplicates()
df = df.sort_values(by=['Title','Platforms'],key=lambda col: col.str.lower())

# Adding completion percentage
for k in range(len(df)):
    obtained = int(df.iloc[k,3])
    total = int(df.iloc[k,4])
    if total == 0:
        df.iloc[k,5] = 'N/A'
    else:
        df.iloc[k,5] = round(obtained/total*100,2)

# Output to csv
df.to_csv(r'outputs/exophase_output.csv',encoding='utf-8',index=False)

driver.quit()