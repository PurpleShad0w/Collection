import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

with open('steam_api_key.txt', 'r') as file:
    API_KEY = file.read()

STEAM_ID = '76561198998679547'
GAMES_URL = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001?key=' + API_KEY + '&include_played_free_games=1&skip_unvetted_apps=0&include_appinfo=1&steamid={}'


response = requests.get(GAMES_URL.format(STEAM_ID))
result = response.json()["response"]["games"]
result = sorted(result, key=lambda g: g["playtime_forever"], reverse=True)
df = pd.json_normalize(result)

caps = DesiredCapabilities().CHROME
caps['pageLoadStrategy'] = 'eager'
driver = webdriver.Chrome(desired_capabilities = caps)

for appid in df['appid']:
    driver.get("https://store.steampowered.com/app/" + str(appid) + "/")

    try:
        select = Select(driver.find_element(By.ID, 'ageYear'))
        select.select_by_value('2000')
        view_button = driver.find_element(By.XPATH, '//*[@id="view_product_page_btn"]')
        view_button.click()
    except:
        pass
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="glanceCtnResponsiveRight"]/div[2]/div[2]/div')))
        tag_button = driver.find_element(By.XPATH, '//*[@id="glanceCtnResponsiveRight"]/div[2]/div[2]/div')
        tag_button.click()
    except:
        pass

    tags = []
    i = 1
    while True:
        try:
            tag_xpath = '//*[@id="app_tagging_modal"]/div/div[2]/div/div[' + str(i) + ']/a'
            tag = driver.find_element(By.XPATH, tag_xpath).text
            tags.append(tag)
            i += 1
        except:
            break
    
    df.loc[df.appid == appid, 'tags'] = ','.join(tags)

tags = sorted((','.join(df['tags'].to_list())).split(','))
tags = list(dict.fromkeys(tags))

playtime_tags = pd.DataFrame(columns=['tag','playtime_minutes','playtime_hours'])

for tag in tags:
    games = df[df['tags'].str.contains(tag)]
    minutes = games['playtime_forever'].sum()
    hours = minutes / 60
    row = [tag, minutes, hours]
    playtime_tags.loc[len(playtime_tags)] = row


playtime_tags.to_csv('outputs/steam_playtime_tags.csv', index=False)