import os
import sys
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))

df = pd.DataFrame(data={'Size':0,'Type':0,'Variation':0,'Name':0,'Total':0,'Big Crown':0,'Small Crown':0,'Largest Size':0,'Smallest Size':0},index=(0,1))

files = os.listdir('outputs')
input = [file for file in files if file.endswith("hunting_log.csv")]
games = []
k = 0

for file in input:
    df_log = pd.read_csv('outputs/'+file)
    names = df_log['Name'].tolist()
    for i in range(len(names)):
        s = pd.Series({'Size':0,'Type':0,'Variation':0,'Name':names[i],'Total':0,'Largest Size':0,'Smallest Size':0})
        df = df.append(s,ignore_index=True)
    file = file.replace('_hunting_log.csv','')
    games.append(file)

df = df.drop_duplicates()

for i in range(len(games)):
    df.insert(i+5,games[i],0)

for file in input:
    df_log = pd.read_csv('outputs/'+file)
    game = games[k]
    k += 1

    for i in range(len(df_log)):
        size = df_log.iloc[i]['Size']
        monster_type = df_log.iloc[i]['Type']
        monster_var = df_log.iloc[i]['Variation']
        name = df_log.iloc[i]['Name']
        hunts = df_log.iloc[i]['Hunted']
        size_big = df_log.iloc[i]['Largest Size']
        size_small = df_log.iloc[i]['Smallest Size']
        big_crown = df_log.iloc[i]['Big Crown']
        small_crown = df_log.iloc[i]['Small Crown']

        df.loc[(df['Name'] == name), [game]] = hunts
        df.loc[(df['Name'] == name), ['Size']] = size
        df.loc[(df['Name'] == name), ['Type']] = monster_type
        df.loc[(df['Name'] == name), ['Variation']] = monster_var

        if df.loc[(df['Name'] == name), ['Largest Size']].to_numpy()[0][0] == 0:
            df.loc[(df['Name'] == name), ['Largest Size']] = size_big
        if df.loc[(df['Name'] == name), ['Smallest Size']].to_numpy()[0][0] == 0:
            df.loc[(df['Name'] == name), ['Smallest Size']] = size_small
        if df.loc[(df['Name'] == name), ['Largest Size']].to_numpy()[0][0] < size_big and size_big != 0:
            df.loc[(df['Name'] == name), ['Largest Size']] = size_big
        if df.loc[(df['Name'] == name), ['Smallest Size']].to_numpy()[0][0] > size_small and size_small != 0:
            df.loc[(df['Name'] == name), ['Smallest Size']] = size_small

        if pd.isna(df.loc[(df['Name'] == name), ['Big Crown']].to_numpy()[0][0]):
            df.loc[(df['Name'] == name), ['Big Crown']] = big_crown
        elif df.loc[(df['Name'] == name), ['Big Crown']].to_numpy()[0][0] == '🥈' and big_crown == '👑':
            df.loc[(df['Name'] == name), ['Big Crown']] = big_crown
        if pd.isna(df.loc[(df['Name'] == name), ['Small Crown']].to_numpy()[0][0]):
            df.loc[(df['Name'] == name), ['Small Crown']] = small_crown

        df.loc[(df['Name'] == name), ['Total']] += hunts


df = df[df['Name'] != 0]
df.to_csv(r'outputs/MH_hunting_table.csv',encoding='utf-8',index=False)