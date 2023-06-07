import os
import sys
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))

import struct
import pymem

import data.monsters as monsters

pm = pymem.Pymem('MonsterHunterWorld.exe')

slot = 1    # change for corresponding save slot in game

rcx = pm.read_long(0x140000000 + 0x5073E80)
rcx = rcx + 0xA8
rcx = pm.read_longlong(rcx)
rdx = 0x27E9F0 * (slot-1)
rcx = rcx + rdx
rcx = rcx + 0xF4EA8

capture_pointer = rcx - 0x4
kill_pointer = capture_pointer + 0x200
large_pointer = capture_pointer + 0xC00
small_pointer = capture_pointer + 0xE00
xp_pointer = capture_pointer + 0x1000
level_pointer = capture_pointer + 0x1200

names = monsters.mhwi_names
small_monsters = monsters.small_monsters

df = pd.DataFrame(data={'ID':0,'Size':0,'Type':0,'Variation':0,'Name':0,'Hunted':0,'Captured':0,'Killed':0,'Big Crown':0,'Small Crown':0,'Largest Size':0,'Smallest Size':0,'XP':0,'Research Level':0},index=(0,1))

for i in range(len(names)):
    capture_pointer += 0x4
    kill_pointer += 0x4
    large_pointer += 0x4
    small_pointer += 0x4
    xp_pointer += 0x4
    level_pointer += 0x4
    caps = pm.read_int(capture_pointer)
    kills = pm.read_int(kill_pointer)
    large = pm.read_int(large_pointer)
    small = pm.read_int(small_pointer)
    xp = pm.read_int(xp_pointer)
    level = pm.read_int(level_pointer)

    if names[i] in small_monsters:
        size = 'Small'
    elif names[i] not in small_monsters and names[i] != '':
        size = 'Large'
    else:
        size = 'Unknown'

    big_crown, small_crown = monsters.find_monster_crowns(names[i], monsters.mhwi_sizes, large, small)

    mtype = monsters.find_monster_type(names[i])

    mvar = monsters.find_monster_variation(names[i])

    hunts = caps + kills

    xp = struct.unpack("@f", struct.pack("@I", xp))[0]

    s = pd.Series({'ID':i,'Size':size,'Type':mtype,'Variation':mvar,'Name':names[i],'Hunted':hunts,'Captured':caps,'Killed':kills,'Big Crown':big_crown,'Small Crown':small_crown,'Largest Size':large,'Smallest Size':small,'XP':xp,'Research Level':level})
    df = df.append(s,ignore_index=True)

df = df[df['Name'] != 0]
df = df[df['Size'] != 'Unknown']

df.to_csv(r'outputs/MHWI_hunting_log.csv',encoding='utf-8',index=False)