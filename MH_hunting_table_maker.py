import os
import sys
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))

df = pd.DataFrame(data={'Size':0,'Type':0,'Name':0,'Total Hunted':0,'Largest Size':0,'Smallest Size':0},index=(0,1))

files = os.listdir('outputs')
input = [file for file in files if file.endswith("hunting_log.csv")]
games = []
k = 0

for file in input:
    df_log = pd.read_csv('outputs/'+file)
    names = df_log['Name'].tolist()
    for i in range(len(names)):
        s = pd.Series({'Size':0,'Type':0,'Name':names[i],'Total Hunted':0,'Largest Size':0,'Smallest Size':0})
        df = df.append(s,ignore_index=True)
    file = file.replace('_hunting_log.csv',' Hunts')
    games.append(file)

df = df.drop_duplicates()

for i in range(len(games)):
    df.insert(i+4,games[i],0)

for file in input:
    df_log = pd.read_csv('outputs/'+file)
    game = games[k]
    k += 1

    for i in range(len(df_log)):
        size = df_log.iloc[i]['Size']
        mtype = df_log.iloc[i]['Type']
        name = df_log.iloc[i]['Name']
        hunts = df_log.iloc[i]['Hunted']
        large_crown = df_log.iloc[i]['Largest Size']
        small_crown = df_log.iloc[i]['Smallest Size']

        df.loc[(df['Name'] == name), [game]] = hunts
        df.loc[(df['Name'] == name), ['Size']] = size
        df.loc[(df['Name'] == name), ['Type']] = mtype

        if df.loc[(df['Name'] == name), ['Largest Size']].to_numpy()[0][0] == 0:
            df.loc[(df['Name'] == name), ['Largest Size']] = large_crown
        if df.loc[(df['Name'] == name), ['Smallest Size']].to_numpy()[0][0] == 0:
            df.loc[(df['Name'] == name), ['Smallest Size']] = small_crown
        if df.loc[(df['Name'] == name), ['Largest Size']].to_numpy()[0][0] < large_crown and large_crown != 0:
            df.loc[(df['Name'] == name), ['Largest Size']] = large_crown
        if df.loc[(df['Name'] == name), ['Smallest Size']].to_numpy()[0][0] > small_crown and small_crown != 0:
            df.loc[(df['Name'] == name), ['Smallest Size']] = small_crown
        
        df.loc[(df['Name'] == name), ['Total Hunted']] += hunts


df = df[df['Name'] != 0]
df.to_csv(r'outputs/MH_hunting_table.csv',encoding='utf-8',index=False)