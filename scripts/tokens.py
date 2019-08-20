import sys, os, re, pprint
# UDPipe tokenize.py
from .helpers import *
from .config import *

from .utils import Batch

def file2fast_text(in_file_1, in_file_2, out_file, empty_dict=None):
    print('Writing:', out_file)
    with open(in_file_1, 'r') as srcf, \
         open(in_file_2, 'r') as trgf, \
         open(out_file, 'w') as outf:
        empty_lines = []
        for i, (src, trg) in enumerate(zip(srcf, trgf)):
            src = src.strip()
            trg = trg.strip()
            if src and trg:
                outf.write(src + ' ||| ' + trg + '\n')
            else:
                empty_lines.append(i)

    if empty_dict != None:
        empty_dict[out_file] = empty_lines

def dir2fast_text(input_dir):
    input_dir, output_dir = create_same_level_output_dir(input_dir, 'merged')
    pairs_dict = get_pairs(input_dir, verbose=False)
    for lang_pair in pairs_dict:
        for lang in lang_pair:
            assert not lang_pair[lang].endswith('.conll'), 'Fast Text format cannot be applied to .conll-files!'
    print('Pairs found:')
    pprint.pprint(pairs_dict)

    print('Merging..')
    empty_dict = {}
    for pair in pairs_dict:
        lang_1, lang_2 = pair.split('-')
        root = root = pairs_dict[pair][lang_1].split('.')[0]
        
        filename_d1 = f'{root}.{lang_1}-{lang_2}'
        outputpath_d1 = os.path.join(output_dir, filename_d1)

        inputpath_l1 = os.path.join(input_dir, pairs_dict[pair][lang_1])
        inputpath_l2 = os.path.join(input_dir, pairs_dict[pair][lang_2])
        file2fast_text(inputpath_l1, inputpath_l2, outputpath_d1, empty_dict)
        

        filename_d2 = f'{root}.{lang_2}-{lang_1}'

        outputpath_d2 = os.path.join(output_dir, filename_d2)
        file2fast_text(inputpath_l2, inputpath_l1, outputpath_d2, empty_dict)
        
    empty_dict_path = os.path.join(output_dir, 'empty.dict')
    with open(empty_dict_path, 'w') as f:
        f.write(repr(empty_dict))
    print('.. done.')
    return output_dir

def align(input_dir, use_shell=False):
    """
        input_dir: token directory
    """

    input_dir = dir2fast_text(input_dir=input_dir)
    # changing input dir to merged_dir for alignment input
    input_dir, output_dir = create_same_level_output_dir(input_dir, 'alignment')

    merged_files = list(filter(lambda x: re.match(r'.*\.[a-z]{2}-[a-z]{2}', x), os.listdir(input_dir)))
    print(f'Valid input files  ("{input_dir}"):')
    pprint.pprint(merged_files)
    print()
    print('Create and submit batchfiles..')
    batch = Batch(name=f'alignment', memory='20GB', log_dir='alignment', timelimit='00:30:00')

    for file in merged_files:
        pair = 'al_'+file.split('.')[-1]
        batch.name = pair
        batch.align(input_dir=input_dir, output_dir=output_dir, filename=file)
        batch.shell() if use_shell else batch.submit()
