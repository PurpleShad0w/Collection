import os
import sys
import pandas as pd
import numpy as np
import warnings
import struct

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))

import data.monsters as monsters

offset_hex = ['0x192B42','0x192C54','0x192D66','0x192D68']
formats = {1:'B', 2:'H', 4:'I', 8:'Q'}
kills, caps, size_small, size_big = [None] * 137, [None] * 137, [None] * 137, [None] * 137

names = monsters.mhgu_names
small_monsters = monsters.small_monsters

df = pd.DataFrame(data={'ID':0,'Size':0,'Name':0,'Hunted':0,'Captured':0,'Killed':0,'Large Crown %':0,'Small Crown %':0},index=(0,1))

with open('inputs/system', mode='rb') as file:
    for i in range(len(names)):
        offset = int(offset_hex[0], 16) + i*2
        file.seek(offset)
        kills[i] = struct.unpack(formats[2], file.read(2))[0]
    
    for i in range(len(names)):
        offset = int(offset_hex[1], 16) + i*2
        file.seek(offset)
        caps[i] = struct.unpack(formats[2], file.read(2))[0]

    for i in range(len(names)):
        offset = int(offset_hex[2], 16) + i*4
        file.seek(offset)
        size_small[i] = struct.unpack(formats[2], file.read(2))[0]
        offset = int(offset_hex[3], 16) + i*4
        file.seek(offset)
        size_big[i] = struct.unpack(formats[2], file.read(2))[0]
    
    for i in range(len(names)):
        hunts = kills[i] + caps[i]
        if names[i] in small_monsters:
            size = 'Small'
        elif names[i] not in small_monsters and names[i] != '':
            size = 'Large'
        else:
            size = 'Unknown'

        s = pd.Series({'ID':i,'Size':size,'Name':names[i],'Hunted':hunts,'Captured':caps[i],'Killed':kills[i],'Large Crown %':size_big[i],'Small Crown %':size_small[i]})
        df = df.append(s, ignore_index=True)

df = df[df['Name'] != 0]
df = df[df['Size'] != 'Unknown']
df.to_csv(r'outputs/MHGU_hunting_log.csv',encoding='utf-8',index=False)