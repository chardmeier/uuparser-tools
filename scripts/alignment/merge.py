import re, os, sys, pprint
from collections import defaultdict

# creates a dictionary with language pairs based on naming convention:
# corpusname.lang1-lang2.lang1
# For example:
# news-commentary-v14.de-en.de and news-commentary-v14.de-en.en
# will be matched in the dictionary

# Arg1: Input directory with sentence aligned and tokenized files
input_dir  = os.path.abspath(sys.argv[1])
# Arg2: Directory where merged files should be saved
write_dir  = os.path.abspath(sys.argv[2])

print('Reading from:')
print(input_dir)
print('Writing merged files to:')
print(write_dir)


if not os.path.isdir(write_dir):
    os.mkdir(write_dir)
    
def get_pairs(path='.', ending=''):
    path = os.path.abspath(path)
    l = os.listdir(path)
    if ending:
        ending=r'\.'+ending
    else:
        ending=''
    l = list(filter(lambda x: re.match(r'.*\.[a-z]{2}-[a-z]{2}\.[a-z]{2}'+ending, x), l))
    pairs_dict = defaultdict(dict)
    if not l:
        print('No valid files found.')
        os.system.exit(0)
    for f in l:    
        #print(f)
        lang = re.findall(r'\.[a-z]{2}-[a-z]{2}\.([a-z]{2})', f)[0]
        pairs_dict[re.findall(r'\.([a-z]{2}-[a-z]{2})\.', f)[0]][lang] = f
    return dict(pairs_dict)

pairs_dict = get_pairs(input_dir)
print('Pairs found:')
pprint.pprint(pairs_dict)

    
def merge(in_file_1, in_file_2, out_file, emtpy_dict=None):
    print('Writing:', out_file)
    with open(in_file_1, 'r', encoding='latin-1') as srcf, \
         open(in_file_2, 'r', encoding='latin-1') as trgf, \
         open(out_file, 'w') as outf:
        empty_lines = []
        for i, (src, trg) in enumerate(zip(srcf, trgf)):
            src = src.strip()
            trg = trg.strip()
            if src and trg:
                outf.write(src + ' ||| ' + trg + '\n')
            else:
                empty_lines.append(i)
                
        if emtpy_dict != None:
            empty_dict[out_file] = empty_lines

print('Merging..')
empty_dict = {}
for pair in pairs_dict:
    lang_1, lang_2 = pair.split('-')
    root = root = pairs_dict[pair][lang_1].split('.')[0]
    
    out_file = f'{write_dir}/{root}.{lang_1}-{lang_2}'
    in_file_1 = os.path.join(input_dir, pairs_dict[pair][lang_1])
    in_file_2 = os.path.join(input_dir, pairs_dict[pair][lang_2])
    merge(in_file_1, in_file_2, out_file, empty_dict)
    
    out_file = f'{write_dir}/{root}.{lang_2}-{lang_1}'
    merge(in_file_2, in_file_1, out_file, empty_dict)
    
with open(f'{write_dir}/empty.dict', 'w') as f:
    f.write(repr(empty_dict))
print('Done.')
    


