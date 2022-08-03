import os
import sys
import json
import pandas as pd
import re
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

os.chdir(os.path.dirname(sys.argv[0]))


def start():
    files = os.listdir('inputs')
    input = [file for file in files if file.endswith(".json")]
    for file in input:
        os.rename('inputs/'+str(file), 'inputs/stats_input.json')


def choose_version():
    with open(r'inputs/stats_input.json') as data_file:    
        data = json.load(data_file)
        if "DataVersion" in str(data):
            return('above')
        else:
            return('below')


def stats_for_1_13_and_above():
    with open(r'inputs/stats_input.json') as data_file:    
        data = json.load(data_file)
    df = pd.json_normalize(data)
    df = df.T
    df = df.drop('DataVersion')
    df.to_csv (r'inputs/stats_raw.csv',header=['values'])
    df = pd.read_csv (r'inputs/stats_raw.csv')
    df.rename(columns={'Unnamed: 0':'stats'},inplace=True)

    # create the necessary dataframes
    df_general = pd.DataFrame(data={'Statistic':'Games quit','Value':0},index=(0,1))
    df_block = pd.DataFrame(data={'Item':'Stone','Mined':0,'Broken':0,'Crafted':0,'Used':0,'Picked Up':0,'Dropped':0},index=(0,1))
    df_entity = pd.DataFrame(data={'Entity':'Creeper','Killed':0,'Killed by':0},index=(0,1))

    # find and collect the statistics
    for i in range(len(df)):
        if df.loc[i,'stats'].startswith('stats.minecraft:mined'):
            block = re.search('stats.minecraft:mined.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stats.minecraft:mined.',''),df.loc[i,'values']],index=['Item','Mined'])
            df_block = df_block.append(s,ignore_index=True)
        if df.loc[i,'stats'].startswith('stats.minecraft:crafted'):
            block = re.search('stats.minecraft:crafted.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stats.minecraft:crafted.',''),df.loc[i,'values']],index=['Item','Crafted'])
            df_block = df_block.append(s,ignore_index=True)
        if df.loc[i,'stats'].startswith('stats.minecraft:picked_up'):
            block = re.search('stats.minecraft:picked_up.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stats.minecraft:picked_up.',''),df.loc[i,'values']],index=['Item','Picked Up'])
            df_block = df_block.append(s,ignore_index=True)
        if df.loc[i,'stats'].startswith('stats.minecraft:used'):
            block = re.search('stats.minecraft:used.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stats.minecraft:used.',''),df.loc[i,'values']],index=['Item','Used'])
            df_block = df_block.append(s,ignore_index=True)
        if df.loc[i,'stats'].startswith('stats.minecraft:dropped'):
            block = re.search('stats.minecraft:dropped.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stats.minecraft:dropped.',''),df.loc[i,'values']],index=['Item','Dropped'])
            df_block = df_block.append(s,ignore_index=True)
        if df.loc[i,'stats'].startswith('stats.minecraft:broken'):
            block = re.search('stats.minecraft:broken.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stats.minecraft:broken.',''),df.loc[i,'values']],index=['Item','Broken'])
            df_block = df_block.append(s,ignore_index=True)
        if df.loc[i,'stats'].startswith('stats.minecraft:killed.'):
            entity = re.search('stats.minecraft:killed.(.*).',df.loc[i,'stats'])
            s = pd.Series([entity.group().replace('stats.minecraft:killed.',''),df.loc[i,'values']],index=['Entity','Killed'])
            df_entity = df_entity.append(s,ignore_index=True)
        if df.loc[i,'stats'].startswith('stats.minecraft:killed_by'):
            entity = re.search('stats.minecraft:killed_by.(.*).',df.loc[i,'stats'])
            s = pd.Series([entity.group().replace('stats.minecraft:killed_by.',''),df.loc[i,'values']],index=['Entity','Killed by'])
            df_entity = df_entity.append(s,ignore_index=True)
        if df.loc[i,'stats'].startswith('stats.minecraft:custom'):
            statistic = re.search('stats.minecraft:custom.(.*).',df.loc[i,'stats'])
            s = pd.Series([statistic.group().replace('stats.minecraft:custom.',''),df.loc[i,'values']],index=['Statistic','Value'])
            df_general = df_general.append(s,ignore_index=True)

    # remove unnecessary columns
    df_block = df_block.iloc[2:]
    df_entity = df_entity.iloc[2:]
    df_general = df_general.iloc[2:]

    # fuze the various statistics
    df_block = df_block.fillna(0)
    df_block = df_block.groupby(df_block['Item']).aggregate({'Mined':'sum','Broken':'sum','Crafted':'sum','Used':'sum','Picked Up':'sum','Dropped':'sum'})
    df_entity = df_entity.fillna(0)
    df_entity = df_entity.groupby(df_entity['Entity']).aggregate({'Killed':'sum','Killed by':'sum'})
    df_general = df_general.fillna(0)
    df_general = df_general.groupby(df_general['Statistic']).aggregate({'Value':'sum'})

    # separate items and mods
    df_block.reset_index(level=0, inplace=True)
    df_block[['Mod', 'Item']] = df_block['Item'].str.split(':', n=1, expand=True)
    df_block = df_block[['Mod','Item','Mined','Broken','Crafted','Used','Picked Up','Dropped']]

    # separate entities and mods
    df_entity.reset_index(level=0, inplace=True)
    df_entity[['Mod', 'Entity']] = df_entity['Entity'].str.split(':', n=1, expand=True)
    df_entity = df_entity[['Mod','Entity','Killed','Killed by']]

    # separate general statistics and mods
    df_general.reset_index(level=0, inplace=True)
    df_general[['Mod', 'Statistic']] = df_general['Statistic'].str.split(':', n=1, expand=True)
    df_general = df_general[['Mod','Statistic','Value']]
    
    # output the excel file
    writer = pd.ExcelWriter(r'outputs/stats_output.xlsx', engine='xlsxwriter')
    df_general.to_excel(writer, sheet_name='General',index=False)
    df_block.to_excel(writer, sheet_name='Items',index=False)
    df_entity.to_excel(writer, sheet_name='Entities',index=False)
    writer.save()


def stats_for_1_12_and_below():
    df = pd.read_json (r'inputs/stats_input.json',typ='series')
    df.to_frame('count')
    df.to_csv (r'inputs/stats_raw.csv',header=['values'])
    df = pd.read_csv (r'inputs/stats_raw.csv')
    df.rename(columns={'Unnamed: 0':'stats'},inplace=True)

    # create the necessary dataframes
    df_general = pd.DataFrame(data={'Statistic':'Games quit','Value':0},index=(0,1))
    df_block = pd.DataFrame(data={'Item':'Stone','Mined':0,'Broken':0,'Crafted':0,'Used':0,'Picked Up':0,'Dropped':0},index=(0,1))
    df_entity = pd.DataFrame(data={'Entity':'Creeper','Killed':0,'Killed by':0},index=(0,1))

    # find and collect the statistics
    for i in range(len(df)):
        if df.loc[i,'stats'].startswith('stat.mineBlock'):
            block = re.search('stat.mineBlock.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stat.mineBlock.',''),df.loc[i,'values']],index=['Item','Mined'])
            df_block = df_block.append(s,ignore_index=True)
            continue
        if df.loc[i,'stats'].startswith('stat.craftItem'):
            block = re.search('stat.craftItem.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stat.craftItem.',''),df.loc[i,'values']],index=['Item','Crafted'])
            df_block = df_block.append(s,ignore_index=True)
            continue
        if df.loc[i,'stats'].startswith('stat.pickup'):
            block = re.search('stat.pickup.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stat.pickup.',''),df.loc[i,'values']],index=['Item','Picked Up'])
            df_block = df_block.append(s,ignore_index=True)
            continue
        if df.loc[i,'stats'].startswith('stat.useItem'):
            block = re.search('stat.useItem.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stat.useItem.',''),df.loc[i,'values']],index=['Item','Used'])
            df_block = df_block.append(s,ignore_index=True)
            continue
        if df.loc[i,'stats'].startswith('stat.drop.'):
            block = re.search('stat.drop.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stat.drop.',''),df.loc[i,'values']],index=['Item','Dropped'])
            df_block = df_block.append(s,ignore_index=True)
            continue
        if df.loc[i,'stats'].startswith('stat.breakItem'):
            block = re.search('stat.breakItem.(.*).',df.loc[i,'stats'])
            s = pd.Series([block.group().replace('stat.breakItem.',''),df.loc[i,'values']],index=['Item','Broken'])
            df_block = df_block.append(s,ignore_index=True)
            continue
        if df.loc[i,'stats'].startswith('stat.killEntity'):
            entity = re.search('stat.killEntity.(.*).',df.loc[i,'stats'])
            s = pd.Series([entity.group().replace('stat.killEntity.',''),df.loc[i,'values']],index=['Entity','Killed'])
            df_entity = df_entity.append(s,ignore_index=True)
            continue
        if df.loc[i,'stats'].startswith('stat.entityKilledBy'):
            entity = re.search('stat.entityKilledBy.(.*).',df.loc[i,'stats'])
            s = pd.Series([entity.group().replace('stat.entityKilledBy.',''),df.loc[i,'values']],index=['Entity','Killed by'])
            df_entity = df_entity.append(s,ignore_index=True)
            continue
        statistic = df.loc[i,'stats'].replace('stat.','')
        s = pd.Series([statistic,df.loc[i,'values']],index=['Statistic','Value'])
        df_general = df_general.append(s,ignore_index=True)

    # remove unnecessary columns
    df_block = df_block.iloc[2:]
    df_entity = df_entity.iloc[2:]
    df_general = df_general.iloc[2:]

    # fuze the various statistics
    df_block = df_block.fillna(0)
    df_block = df_block.groupby(df_block['Item']).aggregate({'Mined':'sum','Broken':'sum','Crafted':'sum','Used':'sum','Picked Up':'sum','Dropped':'sum'})
    df_entity = df_entity.fillna(0)
    df_entity = df_entity.groupby(df_entity['Entity']).aggregate({'Killed':'sum','Killed by':'sum'})
    df_general = df_general.fillna(0)
    df_general = df_general.groupby(df_general['Statistic']).aggregate({'Value':'sum'})

    # separate items and mods
    df_block.reset_index(level=0, inplace=True)
    df_block[['Mod', 'Item']] = df_block['Item'].str.split('.', n=1, expand=True)
    df_block = df_block[['Mod','Item','Mined','Broken','Crafted','Used','Picked Up','Dropped']]
    
    # output the excel file
    writer = pd.ExcelWriter(r'outputs/stats_output.xlsx', engine='xlsxwriter')
    df_general.to_excel(writer, sheet_name='General')
    df_block.to_excel(writer, sheet_name='Items',index=False)
    df_entity.to_excel(writer, sheet_name='Entities')
    writer.save()


start()
if choose_version() == 'above':
    stats_for_1_13_and_above()
elif choose_version() == 'below':
    stats_for_1_12_and_below()
else:
    print('Error: DataVersion not found in input json file')