import sys, os
# UDPipe tokenize.py
from .helpers import default_by_lang, create_dir, udpipe_model_to_code
from .config import *
from .utils import Batch
from .preprocessing import split

def split_and_tokenize(input_file, chunksize, conll=False, nl2x=False):
    part_list = split(input_file, chunksize, conll, nl2x)
    print('Submitting jobs:')
    for part in part_list:
        tokenize(part)
        print()

def tokenize(input_file, model_path=None):
    # arg1: path to file that will be tokenized/tagged
    # input file is expected to end with the respective language for example: abc.xy.en
    input_path = os.path.abspath(input_file)
    print(f'Reading file: {input_path}')
    input_filename = os.path.basename(input_path)
    input_dir = os.path.dirname(input_path)
    output_dir  = os.path.join(input_dir, 'conll')
    output_file = os.path.join(output_dir, f'{input_filename}.conll')
    
    lang = input_filename.split('.')[-1]  
    assert len(lang) == 2, f'Language detection is currently only working with binary language codes such as "de", instead got "{lang}"'
    model_path = default_by_lang(lang)
    lang_code  = udpipe_model_to_code(model_path)

    create_dir(output_dir)
    print(f'Tokenized file will be saved to:', output_dir)

    print(f'Using UDPipe model: {model_path}')

    batch = Batch(name=f'tk_{lang_code}', cpus='2', log_dir='UDPipe')
    batch.tokenize(model_path=model_path, input_path=input_path, output_file=output_file)
    batch.submit()


if __name__ == '__main__':
    tokenize(sys.argv[1])
