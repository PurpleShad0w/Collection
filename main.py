import os
import pandas as pd
import shutil
import warnings

warnings.simplefilter(action='ignore')

path_1 = "C:\\Program Files (x86)\\Steam\\userdata"
path_2 = "552590\\remote"

path_user = os.listdir(path_1)[0]
path = path_1 + "\\" + path_user + "\\" + path_2

slot = int(input("Please insert the slot number you wish to analyze.\n")) - 1
save = "sb_save_slot_" + str(slot) + ".dat"
path_save = path + "\\" + save

shutil.copy(path_save, os.getcwd())

with open(save, 'rb') as file:
    data = file.read().decode('ANSI', errors='ignore')

collectibles = pd.read_csv('collectibles.tsv', sep='\t')

for i in range(0, 61):
    if collectibles['id'][i] in data:
        collectibles['status'][i] = 'Found'
    elif collectibles['id'][i] not in data:
        collectibles['status'][i] = 'Not Found'

collectibles.drop(['id'], axis=1, inplace=True)
collectibles.to_csv('status.csv', index=False)