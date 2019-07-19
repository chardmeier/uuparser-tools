import os, sys
def select_treebank(lang, code2lang, model_dir):
    l = os.listdir(model_dir)
    select = list(filter(lambda key: f'{lang}_' in key, code2lang))
    possible_treebanks = list(map(d.get, select))
    reg_term = f'{possible[0].split('-')[0].lower()}*'
    selected = os.popen(f'du -sh {os.path.join(model_dir, reg_term)}').read().split()[1]
    return selected
    
if __name__ == '__main__':
    SCRIPTS = os.environ['SCRIPTS']
    MODELS = os.environ['MODELS']
    TOKENIZER_NAME = os.environ['TOKENIZER_NAME']
    model_dir = os.path.join(MODELS, TOKENIZER_NAME)
    with open(os.path.join(SCRIPTS, 'code2lang.dict')) as f:
        code2lang = repr(f.read())
    print(select_treebank(sys.argv[1], code2lang, model_dir)
