#!/usr/bin/python
import argparse
import os
d = {}
lang2code = {}
lang2code_trainable = {}

parser = argparse.ArgumentParser(description='Extracts language to code mappings from ud-treebanks')
parser.add_argument('treebank_dir', type=str, help='path to the ud-treebank-directory')
parser.add_argument('--output_dir', '-o', type=str, default='.', help='specifies optional output directory (default=".")')
args = parser.parse_args()

assert os.path.isdir(args.treebank_dir)
print(f'Reading directory: "{args.treebank_dir}"')
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
            lang2code_trainable[curr_dir[3:]] = code
        elif file.endswith('.conllu'):
            code = file.split('-')[0]
            d[curr_dir] = code
            #print(len(path) * '---', file)
            lang2code[curr_dir[3:]] = code
	
import json, pprint

#with open('ud2.4_iso.json', 'w') as json_file:
#    json.dump(d, json_file)

print(f'{len(lang2code)} treebanks found.')
path = os.path.join(args.output_dir, "lang2code.dict")
print(f'Writing to: "{path}"')
with open(path, 'w') as f:
    f.write(pprint.pformat(lang2code))

path = os.path.join(args.output_dir, "lang2code_trainable.dict")
print(f'{len(lang2code_trainable)} trainable treebanks found.')
print(f'Writing to: "{path}"')
with open(path, 'w') as f:
    f.write(pprint.pformat(lang2code_trainable))

