import os
import sys
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))

df = pd.DataFrame(data={'Type':0,'Name':0,'Total Hunted':0,'Large Crown %':0,'Small Crown %':0},index=(0,1))

files = os.listdir('outputs')
input = [file for file in files if file.endswith("hunting_log.csv")]
games = []
k = 0

for file in input:
    df_log = pd.read_csv('outputs/'+file)
    names = df_log['Name'].tolist()
    for i in range(len(names)):
        s = pd.Series({'Type':0,'Name':names[i],'Total Hunted':0,'Large Crown %':0,'Small Crown %':0})
        df = df.append(s,ignore_index=True)
    file = file.replace('_hunting_log.csv',' Hunts')
    games.append(file)

df = df.drop_duplicates()

for i in range(len(games)):
    df.insert(i+3,games[i],0)

for file in input:
    df_log = pd.read_csv('outputs/'+file)
    game = games[k]
    k += 1

    for i in range(len(df_log)):
        size = df_log.iloc[i]['Type']
        name = df_log.iloc[i]['Name']
        hunts = df_log.iloc[i]['Hunted']
        large_crown = df_log.iloc[i]['Large Crown %']
        small_crown = df_log.iloc[i]['Small Crown %']

        df.loc[(df['Name'] == name), [game]] = hunts
        df.loc[(df['Name'] == name), ['Type']] = size

        if df.loc[(df['Name'] == name), ['Large Crown %']].to_numpy()[0][0] == 0:
            df.loc[(df['Name'] == name), ['Large Crown %']] = large_crown
        if df.loc[(df['Name'] == name), ['Small Crown %']].to_numpy()[0][0] == 0:
            df.loc[(df['Name'] == name), ['Small Crown %']] = small_crown
        if df.loc[(df['Name'] == name), ['Large Crown %']].to_numpy()[0][0] < large_crown and large_crown != 0:
            df.loc[(df['Name'] == name), ['Large Crown %']] = large_crown
        if df.loc[(df['Name'] == name), ['Small Crown %']].to_numpy()[0][0] > small_crown and small_crown != 0:
            df.loc[(df['Name'] == name), ['Small Crown %']] = small_crown
        
        df.loc[(df['Name'] == name), ['Total Hunted']] += hunts


df = df[df['Name'] != 0]
df.to_csv(r'outputs/MH_hunting_table.csv',encoding='utf-8',index=False)