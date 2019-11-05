import sys, os, re, pprint
# UDPipe tokenize.py
from .helpers import *
from .config import *

from .utils import Batch



def file2fast_text(in_file_1, in_file_2, out_file, empty_dict=None):
    """
    Converts two tokenized text files into fast_text format
    Empty lines as well original number of lines will be saved to empty_dict dictionary 
    args:
        in_file_1 (string): valid path to file 1
        in_file_2 (string): valid path to file 1
        out_file  (string): path where output should be saved to
        empty_dict  (dict): a dictionary where empty line indeces and number of lines in the input files will be saved to
    """
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
        filename = os.path.basename(out_file)
        if filename.endswith('.fast_text'):
            filename = filename.rsplit('.', 1)[0]
        empty_dict[filename] = empty_lines
        empty_dict[filename+'.no_lines'] = i+1


def dir2fast_text(input_dir):
    """
    Finds language pairs based on notation in form de-en.de, de-en.en and converts them into fast text format using file2fast_text()
    args:
        input_dir (string): path to input directory
    """
    input_dir, output_dir = create_same_level_output_dir(input_dir, 'merged')
    pairs_dict = get_pairs(input_dir, verbose=False)
    for lang_pair in pairs_dict:
        print(lang_pair)
        for lang in pairs_dict[lang_pair]:
            assert not pairs_dict[lang_pair][lang].endswith('.conll'), 'Fast Text format cannot be applied to .conll-files!'
    print('Pairs found:')
    pprint.pprint(pairs_dict)

    print('Merging..')
    empty_dict = {}
    for pair in pairs_dict:
        lang_1, lang_2 = pair.split('-')
        root = root = pairs_dict[pair][lang_1].split('.')[0]
        
        filename_d1 = f'{root}.{lang_1}-{lang_2}.fast_text'
        outputpath_d1 = os.path.join(output_dir, filename_d1)

        inputpath_l1 = os.path.join(input_dir, pairs_dict[pair][lang_1])
        inputpath_l2 = os.path.join(input_dir, pairs_dict[pair][lang_2])
        file2fast_text(inputpath_l1, inputpath_l2, outputpath_d1, empty_dict)
        

        filename_d2 = f'{root}.{lang_2}-{lang_1}.fast_text'

        outputpath_d2 = os.path.join(output_dir, filename_d2)
        file2fast_text(inputpath_l2, inputpath_l1, outputpath_d2, empty_dict)
        
    empty_dict_path = os.path.join(output_dir, 'empty.dict')
    with open(empty_dict_path, 'w') as f:
        f.write(repr(empty_dict))
    print('.. done.')
    return output_dir

def align(input_dir, use_shell=False, args=None):
    """
    Expects 'input_dir' to be the path to the directory with tokens. Tokens will be converted to fast text and saved
    into a directory 'merged'. Batchfiles for alignment jobs will be created and submitted to slurm job system
    args:
        input_dir (string): path to token directory
        use_shell (bool)  : trys to perform alignment in shell instead of slurm sbatch (experimental)
        args (None or argparser.args): additional arguments to modify parameters such es memory, timelimit or partition to run on

    """

    input_dir = dir2fast_text(input_dir=input_dir)
    # changing input dir to merged_dir for alignment input
    input_dir, output_dir = create_same_level_output_dir(input_dir, 'alignment')

    merged_files = list(filter(lambda x: re.match(r'.*\.[a-z]{2}-[a-z]{2}', x), os.listdir(input_dir)))
    print(f'Valid input files  ("{input_dir}"):')
    pprint.pprint(merged_files)
    print()
    print('Create and submit batchfiles..')
    batch = Batch(name=f'alignment', memory='10GB', log_dir='alignment', timelimit='04:00:00', args=args)

    for filename in merged_files:
        outputname = filename
        if filename.endswith('.fast_text'):
            outputname = filename.rsplit('.', 1)[0]
        pair = 'al_'+outputname.split('.')[-1]
        batch.name = pair

        batch.align(input_dir=input_dir, output_dir=output_dir, filename=filename, outputname=outputname)
        batch.shell() if use_shell else batch.submit()
