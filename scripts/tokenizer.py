import sys, os, ntpath
# UDPipe tokenize.py
from .helpers import default_by_lang, create_dir, udpipe_model_to_code
from .config import *
from .utils import Batch

def tokenize(arg1, model_path=None):
    # arg1: path to file that will be tokenized/tagged
    # input file is expected to end with the respective language for example: abc.xy.en
    input_path = os.path.abspath(arg1)
    print(f'Reading file: {input_path}')
    input_filename = ntpath.basename(input_path)
    input_dir = os.path.dirname(input_path)
    output_dir  = os.path.join(input_dir, 'conll')
    output_file = os.path.join(output_dir, f'{input_filename}.conll')
    
    lang = input_filename.split('.')[-1]  
    assert len(lang) == 2, f'Language detection is currently only working with binary language codes such as "de", instead got "{lang}"'
    model_path = default_by_lang(lang)
    lang_code  = udpipe_model_to_code(model_path)

    create_dir(output_dir)
    print(f'Tokenized file will be saved to:')

    print(f'Using UDPipe model: {model_path}')

    log_path = f"{LOGS}/UDPipe"
    create_dir(log_path)

    batch = Batch(name=f'tk_{lang_code}', memory='16GB', log_path=log_path)
    batch.tokenize(model_path=model_path, input_path=input_path, output_file=output_file)
    batch.submit()

if __name__ == '__main__':
    tokenize(sys.argv[1])
