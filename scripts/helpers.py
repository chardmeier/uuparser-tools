import os, sys, ntpath
from .config import SCRIPTS, MODELS, TOKENIZER_NAME, BATCHFILES, code2lang


def select_treebank(lang, model_dir):
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
    return select_treebank(lang, tokenizer_model_dir)

def udpipe_model_to_code(path):
    file = ntpath.basename(path)
    lang_code = list(filter(lambda x: file.startswith(x[1].lower()), code2lang.items()))[0][0]
    return lang_code


def create_dir(dir_path):
    if not os.path.isdir(dir_path):
        print('Create directory:', dir_path)
        os.mkdir(dir_path)

def submit_job(batch_path):
    shell_output = os.popen(f'sbatch {batch_path}').read()
    print(shell_output)
    job_id       = shell_output.split()[-1]
    with open(batch_path) as f:
        batch_string = f.read()
    batch_history_dir = os.path.join(BATCHFILES, 'history')
    create_dir(batch_history_dir)

    batch_history_path = os.path.join(batch_history_dir, f"{job_id}.sh")
    with open(batch_history_path, 'w') as f:
        batch_string = f.write(batch_string)

    print(f'Batchfile location: {batch_history_path}')


