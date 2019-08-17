import os, sys, ntpath
from .config import SCRIPTS, MODELS, TOKENIZER_NAME, BATCHFILES, code2lang

def handle_split(input_dir, match_string, do):
    """Collects all files from the input_dir matching with match_string and handing over to do=func()"""
    assert os.path.isdir(input_dir), f'Directory not found: {input_dir}'
    files = os.listdir(input_dir)
    part_files = list(filter(lambda x: re.match(fr'PART_\d+___.*{match_string}.*\.conll', x), files))
    print('Found parts:')
    pprint.pprint(part_files)
    for file in part_files:
        do(os.path.join(input_dir, file))
        print()


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
    tokenizer_model_dir = os.path.join(MODELS, TOKENIZER_NAME)
    return udpipe_select_model(lang, tokenizer_model_dir)

def udpipe_model_to_code(path):
    file = ntpath.basename(path)
    lang_code = list(filter(lambda x: file.startswith(x[1].lower()), code2lang.items()))[0][0]
    return lang_code


def create_dir(dir_path):
    if not os.path.isdir(dir_path):
        print('Create directory:', dir_path)
        os.mkdir(dir_path)



