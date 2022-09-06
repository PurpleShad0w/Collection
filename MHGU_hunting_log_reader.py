import os
import sys
import pandas as pd
import numpy as np
import warnings
import struct

warnings.simplefilter(action='ignore', category=FutureWarning)
os.chdir(os.path.dirname(sys.argv[0]))


offset_hex = ['0x192B42','0x192C54','0x192D66','0x192D68']
formats = {1:'B', 2:'H', 4:'I', 8:'Q'}
hunts, caps, size_small, size_big = [None] * 137, [None] * 137, [None] * 137, [None] * 137

names = ["Rathian", "Gold Rathian", "Dreadqueen Rathian", "Rathalos", "Silver Rathalos", "Dreadking Rathalos", "Khezu", "Yian Kut-Ku", "Gypceros",
        "Plesioth", "Kirin", "Velocidrome", "Gendrome", "Iodrome", "Cephadrome", "Yian Garuga", "Deadeye Yian Garuga", "Daimyo Hermitaur",
        "Stonefist Hermitaur", "Shogun Ceanataur", "Blangonga", "Rajang", "Furious Rajang", "Kushala Daora", "Chameleos", "Teostra", "Bulldrome",
        "Tigrex", "Grimclaw Tigrex", "Akantor", "Lavasioth", "Nargacuga", "Silverwind Nargacuga", "Ukanlos", "Deviljho", "Savage Deviljho",
        "Uragaan", "Crystalbeard Uragaan", "Lagiacrus", "Royal Ludroth", "Agnaktor", "Alatreon", "Duramboros", "Nibelsnarf", "Zinogre",
        "Thunderlord Zinogre", "Amatsu", "Arzuros", "Redhelm Arzuros", "Lagombi", "Snowbaron Lagombi", "Volvidon", "Brachydios", "Kecha Wacha",
        "Tetsucabra", "Drilltusk Tetsucabra", "Zamtrios", "Najarala", "Seltas Queen", "Gore Magala", "Shagaru Magala", "Seltas", "Seregios",
        "Malfestio", "Glavenus", "Hellblade Glavenus", "Astalos", "Mizutsune", "Gammoth", "Nakarkos", "Great Maccao", "Aptonoth",
        "Apceros", "Kelbi", "Mosswine", "Hornetaur", "Vespoid", "Felyne", "Melynx", "Velociprey", "Genprey",
        "Ioprey", "Cephalos", "Bullfango", "Popo", "Giaprey", "Anteka", "Remobra", "Hermitaur", "Ceanataur",
        "Blango", "Rhenoplos", "Bnahabra", "Altaroth", "Jaggi", "Jaggia", "Ludroth", "Uroktor", "Slagtoth",
        "Gargwa", "Zamite", "Konchu", "Maccao", "Larinoth", "Moofah", "", "", "",
        "", "", "", "", "Basarios", "Gravios", "Diablos", "Bloodbath Diablos", "Lao-Shan Lung",
        "Fatalis", "Crimson Fatalis", "White Fatalis", "Rustrazor Ceanataur", "Congalala", "Giadrome", "Barioth", "Barroth", "Raging Brachydios",
        "Nerscylla", "Chaotic Gore Magala", "Nightcloak Malfestio", "Boltreaver Astalos", "Soulseer Mizutsune", "Elderfrost Gammoth", "Valstrax", "", "Ahtal-Ka",
        "Great Thunderbug", "Conga"]

small_monsters = ['Altaroth', 'Anteka', 'Apceros', 'Aptonoth', 'Blango', 'Bnahabra', 'Bullfango', 'Ceanataur', 'Cephalos',
                 'Conga', 'Felyne', 'Gargwa', 'Genprey', 'Giaprey', 'Great Thunderbug', 'Hermitaur', 'Hornetaur', 'Ioprey',
                 'Jaggi', 'Jaggia', 'Kelbi', 'Konchu', 'Larinoth', 'Ludroth', 'Maccao', 'Melynx', 'Moofah', 
                 'Mosswine', 'Popo', 'Remobra', 'Rhenoplos', 'Slagtoth', 'Uroktor', 'Velociprey', 'Vespoid', 'Zamite']

df = pd.DataFrame(data={'ID':0,'Type':0,'Name':0,'Hunted':0,'Captured':0,'Killed':0,'Large Crown %':0,'Small Crown %':0},index=(0,1))

with open('inputs/system', mode='rb') as file:
    for i in range(len(names)):
        offset = int(offset_hex[0], 16) + i*2
        file.seek(offset)
        hunts[i] = struct.unpack(formats[2], file.read(2))[0]
    
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
        kills = hunts[i] - caps[i]
        if names[i] in small_monsters:
            size = 'Small'
        elif names[i] not in small_monsters and names[i] != '':
            size = 'Large'
        else:
            size = 'Unknown'

        s = pd.Series({'ID':i,'Type':size,'Name':names[i],'Hunted':hunts[i],'Captured':caps[i],'Killed':kills,'Large Crown %':size_big[i],'Small Crown %':size_small[i]})
        df = df.append(s, ignore_index=True)

df = df[df['Name'] != 0]
df.to_csv(r'outputs/MHGU_hunting_log.csv',encoding='utf-8',index=False)