import pandas as pd
import json
import re
import os
import sys

os.chdir(os.path.dirname(sys.argv[0]))

# import and treat the json file
def stats():
    with open(r'input.json') as data_file:    
        data = json.load(data_file)
    df = pd.json_normalize(data)
    df = df.T
    df = df.drop('DataVersion')
    df.to_csv (r'raw.csv',header=['values'])
    df = pd.read_csv (r'raw.csv')
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
    writer = pd.ExcelWriter(r'output.xlsx', engine='xlsxwriter')
    df_general.to_excel(writer, sheet_name='General',index=False)
    df_block.to_excel(writer, sheet_name='Items',index=False)
    df_entity.to_excel(writer, sheet_name='Entities',index=False)
    writer.save()