#!/usr/bin/python
import argparse
import os
d = {}
lang2code = {}

parser = argparse.ArgumentParser(description='Extracts language to code mappings from ud-treebanks')
parser.add_argugment('treebank_dir', type=str, help='path to the ud-treebank-directory')
parser.add_argugment('--output', '-o', type=str, default='lang2code.dict', help='specifies optional output path (default="lang2code.dict")')
args = parser.parse_args()

assert os.path.isdir(args.treebank_dir)
count = 0
# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk(args.treebank_dir):
    path = root.split(os.sep)
    #print((len(path) - 1) * '---', os.path.basename(root))
    curr_dir = os.path.basename(root)
    if not curr_dir.startswith('UD_'):
        continue
    for file in files:
        if file.endswith('ud-train.conllu'):
            code = file.split('-')[0]
            d[curr_dir] = code
            #print(len(path) * '---', file)
            lang2code[curr_dir[3:]] = code
	
import json

#with open('ud2.4_iso.json', 'w') as json_file:
#    json.dump(d, json_file)


with open(args.output, 'w') as f:
    f.write(repr(lang2code))