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

GAMES_URL = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001?key={}'
GAMES_URL = GAMES_URL.format(API_KEY)
GAMES_URL = GAMES_URL + '&include_played_free_games=1&skip_unvetted_apps=0&include_appinfo=1&steamid={}'
GAMES_URL = GAMES_URL.format(STEAM_ID)

ACHIEV_URL = '&key=' + API_KEY + '&steamid=' + STEAM_ID
ACHIEV_URL = 'https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={}' + ACHIEV_URL


response = requests.get(GAMES_URL)
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

driver.quit()

for appid in df['appid']:
    response = requests.get(ACHIEV_URL.format(appid))

    try:
        result = response.json()['playerstats']['achievements']
        achievements = pd.json_normalize(result)
        unlocked = len(achievements[achievements.achieved == 1])
        locked = len(achievements[achievements.achieved == 0])
        total = unlocked + locked
        perfect = 0

        if unlocked == total:
            perfect = 1

    except KeyError:
        unlocked, locked, total, perfect = 0, 0, 0, 0

    df.loc[df.appid == appid, 'achiev_unlocked'] = unlocked
    df.loc[df.appid == appid, 'achiev_locked'] = locked
    df.loc[df.appid == appid, 'achiev_total'] = total
    df.loc[df.appid == appid, 'achiev_perfect'] = perfect

tags = sorted((','.join(df['tags'].to_list())).split(','))
tags = list(dict.fromkeys(tags))

tags_ranking = pd.DataFrame(columns=['tag','playtime_minutes','playtime_hours','total_achievs','total_perfects'])

for tag in tags:
    games = df[df['tags'].str.contains(tag)]
    minutes = games['playtime_forever'].sum()
    hours = minutes / 60
    achievs = games['achiev_unlocked'].sum()
    perfects = games['achiev_perfect'].sum()
    row = [tag, minutes, hours, achievs, perfects]
    tags_ranking.loc[len(tags_ranking)] = row

tags_ranking = tags_ranking.iloc[1:]

tags_ranking = tags_ranking.sort_values(by='playtime_minutes', ascending=False)
tags_ranking.reset_index(inplace=True)
tags_ranking['rank_playtime'] = tags_ranking.index + 1
tags_ranking.drop(columns='index', inplace=True)

tags_ranking = tags_ranking.sort_values(by='total_achievs', ascending=False)
tags_ranking.reset_index(inplace=True)
tags_ranking['rank_achievs'] = tags_ranking.index + 1
tags_ranking.drop(columns='index', inplace=True)

tags_ranking = tags_ranking.sort_values(by='total_perfects', ascending=False)
tags_ranking.reset_index(inplace=True)
tags_ranking['rank_perfects'] = tags_ranking.index + 1
tags_ranking.drop(columns='index', inplace=True)

tags_ranking['overall_rank'] = tags_ranking[['rank_playtime', 'rank_achievs', 'rank_perfects']].mean(axis=1)

tags_ranking.to_csv('outputs/steam_tags_ranking.csv', index=False)