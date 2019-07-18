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
            code = file.split('-')[0]
            d[curr_dir] = code
            print(len(path) * '---', file)
            print(curr_dir[3:], code)
	
import json

with open('ud2.4_iso.json', 'w') as json_file:
    json.dump(d, json_file)
