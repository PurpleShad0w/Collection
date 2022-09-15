import os
import sys
import pandas as pd
import numpy as np
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))

import struct
from ReadWriteMemory import ReadWriteMemory
import pymem

import data.monsters as monsters

rwm = ReadWriteMemory()

process = rwm.get_process_by_name('MonsterHunterWorld.exe')
process.open()
pm = pymem.Pymem('MonsterHunterWorld.exe')

slot = 1    # change for corresponding save slot in game

# process_id = hex(process.pid)
# process_id = '140000000'
# 140000000
# rcx = int(process_id, 16) + int('0x5073E80', 16)
# 145073E80
rcx = pm.read_long(0x145073E80)
rcx = rcx + int('0xA8', 16)
rcx = process.read(int(hex(rcx), 16))
rdx = '0x27E9F0'
rdx = int(rdx, 16) * (slot-1)
rcx = rcx + rdx
rcx = rcx + int('0xF4EA8', 16)

# script to find list of pointers and thus the static address, 0xBE4F28
# pointers = []
# for i in range(65535):
#     h = hex(i)
#     h = h + '4F28'
#     if process.read(int(h, 16)) == 1:
#         pointers.append(h)
# np.savetxt('pointers.csv', pointers, delimiter=',', fmt='%s')

rcx = rcx - 4

capture_pointer = process.get_pointer(int(hex(rcx), 16))
kill_pointer = process.get_pointer(capture_pointer+0x200)
large_pointer = process.get_pointer(capture_pointer+0xC00)
small_pointer = process.get_pointer(capture_pointer+0xE00)
xp_pointer = process.get_pointer(capture_pointer+0x1000)
level_pointer = process.get_pointer(capture_pointer+0x1200)

names = monsters.mhwi_names
small_monsters = monsters.small_monsters

df = pd.DataFrame(data={'ID':0,'Type':0,'Name':0,'Hunted':0,'Captured':0,'Killed':0,'Large Crown %':0,'Small Crown %':0,'XP':0,'Research Level':0},index=(0,1))

for i in range(len(names)):
    capture_pointer = process.get_pointer(capture_pointer + 0x4)
    kill_pointer = process.get_pointer(kill_pointer + 0x4)
    large_pointer = process.get_pointer(large_pointer + 0x4)
    small_pointer = process.get_pointer(small_pointer + 0x4)
    xp_pointer = process.get_pointer(xp_pointer + 0x4)
    level_pointer = process.get_pointer(level_pointer + 0x4)
    caps = process.read(capture_pointer)
    kills = process.read(kill_pointer)
    large = process.read(large_pointer)
    small = process.read(small_pointer)
    xp = process.read(xp_pointer)
    level = process.read(level_pointer)

    if names[i] in small_monsters:
        size = 'Small'
    elif names[i] not in small_monsters and names[i] != '':
        size = 'Large'
    else:
        size = 'Unknown'

    hunts = caps + kills

    xp = struct.unpack("@f", struct.pack("@I", xp))[0]

    s = pd.Series({'ID':i,'Type':size,'Name':names[i],'Hunted':hunts,'Captured':caps,'Killed':kills,'Large Crown %':large,'Small Crown %':small,'XP':xp,'Research Level':level})
    df = df.append(s,ignore_index=True)

df = df[df['Name'] != 0]
df = df[df['Type'] != 'Unknown']

df.to_csv(r'outputs/MHWI_hunting_log.csv',encoding='utf-8',index=False)