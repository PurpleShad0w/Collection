import os
import sys
import scripts.input as input
import scripts.stats_for_1_13_and_above as stats_for_1_13_and_above
import scripts.stats_for_1_12_and_below as stats_for_1_12_and_below
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

os.chdir(os.path.dirname(sys.argv[0]))

input.start()
if input.choose_version() == 'above':
    stats_for_1_13_and_above.stats()
elif input.choose_version() == 'below':
    stats_for_1_12_and_below.stats()
else:
    print('Error: DataVersion not found in input.json')