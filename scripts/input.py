import os
import sys
import pandas as pd
import json

os.chdir(os.path.dirname(sys.argv[0]))

def start():
    files = os.listdir('.')
    input = [file for file in files if file.endswith(".json")]
    for file in input:
        os.rename(file, 'input.json')

def choose_version():
    with open(r'input.json') as data_file:    
        data = json.load(data_file)
        if "DataVersion" in str(data):
            return('above')
        else:
            return('below')