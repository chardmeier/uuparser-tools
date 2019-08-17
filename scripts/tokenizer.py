import sys, os, ntpath
# UDPipe tokenize.py
from .helpers import default_by_lang, create_dir, udpipe_model_to_code
from .config import *
from .utils import Batch
from .preprocessing import split

def split_and_tokenize(input_file, chunksize, conll=False, double_n=False):
    part_list = split(input_file, chunksize, conll, double_n)
    print('Submitting jobs:')
    for part in part_list:
        tokenize(part)
        print()

def tokenize(input_file, model_path=None):
    # arg1: path to file that will be tokenized/tagged
    # input file is expected to end with the respective language for example: abc.xy.en
    input_path = os.path.abspath(input_file)
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
    print(f'Tokenized file will be saved to:', output_dir)

    print(f'Using UDPipe model: {model_path}')

    log_path = f"{LOGS}/UDPipe"
    create_dir(log_path)

    batch = Batch(name=f'tk_{lang_code}', memory='16GB', log_path=log_path)
    batch.tokenize(model_path=model_path, input_path=input_path, output_file=output_file)
    batch.submit()

def extract_tokens(arg1):
    # Script takes conll file output by udpipe and extracts the tokenized tokens.
    # Newline will only be added if SpacesAfter is '\n'
    input_path = os.path.abspath(arg1)
    print(f'Reading file: {input_path}')
    input_filename = ntpath.basename(input_path)
    input_dir = os.path.dirname(input_path)
    output_dir  = os.path.join(input_dir, 'tokens')
    create_dir(output_dir)
    print(f'Tokens will be saved to:', output_dir)

    assert input_filename.endswith('.conll')
    output_file  = '.'.join(file.split('.')[:-1] + ['txt']) 
    output_path  = os.path.join(output_dir, output_file)

    with open(file) as f:
        print('Opening file:', file)
        lines = []
        line  = []
        for token_line in f:
            if (not token_line.startswith('#')) and (token_line != '\n'): # ignores newlines and those starting with #
                token_line = token_line.split('\t')
                line_no, token = token_line[0], token_line[1] # extract token
                if not ('-' in line_no):
                    line.append(token_line[1])                # adding token to current line

                if token_line[9].split('=')[-1] == '\\n\n':   # checks for newline
                    lines.append(' '.join(line) + '\n')       # joins tokens with newline at the end
                    line = []                                 # initialize new line
    
    with open(output_path, 'w') as f:
        print('Writing tokens to:', output_path)
        f.writelines(lines)

if __name__ == '__main__':
    tokenize(sys.argv[1])
