#!/usr/bin/python
import argparse
import os
d = {}
code2lang = {}
code2lang_trainable = {}
SCRIPTS = os.environ['SCRIPTS'] # ToDO change to CONFIGS!
assert bool(SCRIPTS), "Environment variable $SCRIPT not found!"

parser = argparse.ArgumentParser(description='Extracts language to code mappings from ud-treebanks')
parser.add_argument('treebank_dir', type=str, help='path to the ud-treebank-directory')
parser.add_argument('--output_dir', '-o', type=str, default=SCRIPTS, help='specifies optional output directory (default=".")')
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
            code2lang_trainable[code] = curr_dir[3:]
        elif file.endswith('.conllu'):
            code = file.split('-')[0]
            d[curr_dir] = code
            #print(len(path) * '---', file)
            code2lang[code] = curr_dir[3:]
    
import json, pprint

#with open('ud2.4_iso.json', 'w') as json_file:
#    json.dump(d, json_file)

print(f'{len(code2lang)} treebanks found.')
path = os.path.join(args.output_dir, "code2lang.dict")
print(f'Writing to: "{path}"')
with open(path, 'w') as f:
    f.write(pprint.pformat(code2lang))

path = os.path.join(args.output_dir, "code2lang_trainable.dict")
print(f'{len(code2lang_trainable)} trainable treebanks found.')
print(f'Writing to: "{path}"')
with open(path, 'w') as f:
    f.write(pprint.pformat(code2lang_trainable))

