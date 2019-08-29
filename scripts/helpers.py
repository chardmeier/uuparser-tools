import os, sys, ntpath, pprint
import re
from collections import defaultdict


from .config import SCRIPTS, MODELS, NAME_TOKENIZER, BATCHFILES, code2lang

def save_dict(dict_path, dict_data, verbose=True):
    dict_path = os.path.abspath(dict_path) # dictionary path
    d = {}
    if os.path.isfile(dict_path):
        with open(dict_path) as f:    # reading out existing data
            file_data = f.read()
            if file_data:
                try:
                    d = eval(f.read())
                except SyntaxError as e:
                    print('Cannot read dictionary:')
                    print(file_data)
                    raise(e)

    with open(dict_path, 'w') as f:   # writing new / updated data
        d.update(dict_data)
        f.write(repr(d))
    if verbose:
        print('Saved:', dict_path)




def get_pairs(input_dir, ending='', verbose=False):
    input_dir = os.path.abspath(input_dir)
    files = os.listdir(input_dir)
    import pprint
    if verbose:
        print('Files found in:', input_dir)
        pprint.pprint(files)
    if ending:
        ending=r'\.'+ending.lstrip('.')
    else:
        ending=''
    pair_files = list(filter(lambda x: re.match(r'.*\.?[a-z]{2}-[a-z]{2}\.[a-z]{2}'+ending+r'\b', x) and (not x.startswith('PART_')), files))
    pairs_dict = defaultdict(dict)
    if not pair_files:
        raise(ValueError('No valid files found.'))
    for file in pair_files:    
        #print(f)
        lang = re.findall(r'[a-z]{2}-[a-z]{2}\.([a-z]{2})', file)[0]
        pairs_dict[re.findall(r'([a-z]{2}-[a-z]{2})\.', file)[0]][lang] = file
    return dict(pairs_dict)

def get_conlls(input_dir, exclude_parts=True, verbose=True):
    files = os.listdir(input_dir)
    conll_files = list(filter(lambda f: f.endswith('.conll'), files))
    if exclude_parts:
        conll_files = list(filter(lambda f: (not f.startswith('PART_')), conll_files))
    print('Found .conll files:',)
    conll_files.sort()
    pprint.pprint(conll_files)
    return conll_files

def get_split_files(input_dir, match_string, verbose=True):
    files = os.listdir(input_dir)
    full_match_string = fr'PART_\d+___.*{match_string}.*\.conll'
    part_files = list(filter(lambda x: re.match(full_match_string, x), files))
    part_files.sort(key=lambda x: int(x.split('_')[1]))
    if verbose:
        print('Input:', match_string)
        print('Full match-string:', full_match_string)
        print(f'Found parts in "{input_dir}":')
        pprint.pprint(part_files)
    assert part_files, 'No valid files found!'
    return part_files

def handle_split(input_dir, match_string, do, args=None):
    """Collects all files from the input_dir matching with match_string and handing over to do=func()"""
    assert os.path.isdir(input_dir), f'Directory not found: {input_dir}'
    part_files = get_split_files(input_dir, match_string)

    for file in part_files:
        if args:
            do(os.path.join(input_dir, file), args=args)
        else:
            do(os.path.join(input_dir, file))
        print()

def create_same_level_output_dir(input_dir, output_dir_name, verbose=True):
    input_dir = os.path.abspath(input_dir)
    assert os.path.isdir(input_dir), f'Input needs to be a directory: {input_dir}'

    output_dir  = os.path.abspath(os.path.join(input_dir, '..', output_dir_name))
    create_dir(output_dir)

    if verbose:
        print('Input directory: ', input_dir)
        print('Output directory:', output_dir)
        print()
    return input_dir, output_dir


def udpipe_select_model(lang, model_dir):
    """
        lang:      (string) langauge code e.g. "de", "en", "fr"
        model_dir: (string) directory with pre-trained UDPipe models e.g. "english-ewt-ud-2.4-190531.udpipe"
        Effect:
            Selects the largest treebank model within the given directory
    """
    #print(model_dir, lang)
    l = os.listdir(model_dir)
    select = list(filter(lambda key: f'{lang}_' in key, code2lang)) # select all keys for this language in code2lang.dict
    #print(select)
    assert bool(select), f'No models found for for language {lang}'
    possible_treebanks = list(map(code2lang.get, select))           # convert lang short cut to language file name as used by udpipe pre-trained models
    #print(possible_treebanks)
    reg_term = f'{possible_treebanks[0].split("-")[0].lower()}*'
    selected = os.popen(f'du -sh {os.path.join(model_dir, reg_term)}').read().split()[1]
    return selected
    
def default_by_lang(lang):
    tokenizer_model_dir = os.path.join(MODELS, NAME_TOKENIZER)
    return udpipe_select_model(lang, tokenizer_model_dir)

def udpipe_model_to_code(path):
    file = ntpath.basename(path)
    lang_code = list(filter(lambda x: file.startswith(x[1].lower()), code2lang.items()))[0][0]
    return lang_code


def create_dir(dir_path):
    if not os.path.isdir(dir_path):
        print('Create directory:', dir_path)
        os.mkdir(dir_path)



