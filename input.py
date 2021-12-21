import os
import sys

os.chdir(os.path.dirname(sys.argv[0]))

files = os.listdir('.')
input = [file for file in files if file.endswith(".json")]
for file in input:
    os.rename(file, 'input.json')