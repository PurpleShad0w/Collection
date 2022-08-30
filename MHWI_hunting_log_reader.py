import os
import sys
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))

import struct
from ReadWriteMemory import ReadWriteMemory

rwm = ReadWriteMemory()

process = rwm.get_process_by_name('MonsterHunterWorld.exe')
process.open()

capture_pointer = process.get_pointer(0x6DE24F24, offsets=[0x9BFA4F24])
kill_pointer = process.get_pointer(capture_pointer+0x200)
large_pointer = process.get_pointer(capture_pointer+0xC00)
small_pointer = process.get_pointer(capture_pointer+0xE00)
xp_pointer = process.get_pointer(capture_pointer+0x1000)
level_pointer = process.get_pointer(capture_pointer+0x1200)

names = ['Anjanath',
        'Rathalos','Aptonoth','Jagras','Zorah Magdaros','Mosswine','Gajau','Great Jagras','Kestodon (male)','Rathian','Pink Rathian',
        'Azure Rathalos','Diablos','Black Diablos','Kirin','Behemoth','Kushala Daora','Lunastra','Teostra','Lavasioth','Deviljho',
        'Barroth','Uragaan','Leshen','Pukei-Pukei','Nergigante',"Xeno'jiiva",'Kulu-Ya-Ku','Tzitzi-Ya-Ku','Jyuratodus','Tobi-Kadachi',
        'Paolumu','Legiana','Great Girros','Odogaron','Radobaan','Vaal Hazak','Dodogama','Kulve Taroth','Bazelgeuse','Apceros',
        'Kelbi (male)','Kelbi (female)','Hornetaur','Vespoid','Mernos','Kestodon (female)','Raphinos','Shamos','Barnos','Girros',
        'Ancient Leshen','Gastodon','Noios','','','Gajalaka','','','','',
        'Tigrex','Nargacuga','Barioth','Savage Deviljho','Brachydios','Glavenus','Acidic Glavenus','Fulgur Anjanath','Coral Pukei-Pukei','Ruiner Nergigante',
        'Viper Tobi-Kadachi','Nightshade Paolumu','Shrieking Legiana','Ebony Odogaron','Blackveil Vaal Hazak','Seething Bazelgeuse','Beotodus','Banbaro','Velkhana','Namielle',
        'Shara Ishvalda','Popo','Anteka','Wulg','Cortos','Boaboa','Alatreon','Gold Rathian','Silver Rathalos','Yian Garuga',
        'Rajang','Furious Rajang','Brute Tigrex','Zinogre','Stygian Zinogre','Raging Brachydios',"Safi'jiiva",'','Scarred Yian Garuga','Frostfang Barioth',
        'Fatalis']

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

    if kills > 0 and level == 0:
        size = 'Small'
    elif names[i] != '':
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