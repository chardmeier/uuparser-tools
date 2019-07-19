import os, sys
from .config import SCRIPTS, MODELS, TOKENIZER_NAME


def select_treebank(lang, code2lang, model_dir):
    #print(model_dir, lang)
    l = os.listdir(model_dir)
    select = list(filter(lambda key: f'{lang}_' in key, code2lang)) # select all keys for this language in code2lang.dict
    #print(select)
    assert bool(select), f'No models found for for language {lang}'
    possible_treebanks = list(map(code2lang.get, select))           # convert lang short cut to language file name as used by udpipe pre-trained models
    #print(possible_treebanks)
    reg_term = f'{possible_treebanks[0].split("-")[0].lower()}*'
    selected = os.popen(f'du -sh {os.path.join(model_dir, reg_term)}').read().split()[1]
    return os.path.abspath(selected)
    
def default_by_lang(lang):
    tokenizer_model_dir = os.path.join(MODELS, TOKENIZER_NAME)
    with open(os.path.join(SCRIPTS, 'code2lang.dict')) as f:
        code2lang = eval(f.read())
    return select_treebank(lang, code2lang, tokenizer_model_dir)


def create_dir(dir_path):
    if not os.path.isdir(dir_path):
        print('Create directory:', dir_path)
        os.mkdir(dir_path)