#!/usr/bin/python

import os
d = {}
# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk("ud-treebanks-v2.4"):
    path = root.split(os.sep)
    print((len(path) - 1) * '---', os.path.basename(root))
    curr_dir = os.path.basename(root)
    for file in files:
        if file.endswith('ud-train.conllu'):
            d[curr_dir] = file.split('-')[0]
            print(len(path) * '---', file)
	
import json

with open('ud2.4_iso.json', 'w') as json_file:
    json.dump(d, json_file)
