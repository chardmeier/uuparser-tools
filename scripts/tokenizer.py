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
    #main_dir  = os.path.abspath(sys.argv[1])

    # set ending of output files  (dot (.) must be included !):
    ending = '' # '.token'

    #input_dir = os.path.join(main_dir, 'conll')
    input_dir = os.path.abspath(arg1)
    assert os.path.isdir(input_dir)

    output_dir  = os.path.join(main_dir, 'tokens')

    create_dir(output_dir)

    print('Loading directory: ', input_dir)

    files = list(filter(lambda f: f.endswith('.conll'), os.listdir(input_dir)))
    print('Found .conll files:',)
    pprint.pprint(files)
    print()
    print('Output directory:', output_dir)
    print()
    for file in files:
        in_path = os.path.join(input_dir, file)
        with open(in_path) as f:
            print('Reading file:', in_path)
            lines = []
            line  = []
            for token_line in f:
                if (not token_line.startswith('#')) and (token_line != '\n'):
                    token_line = token_line.split('\t')
                    line_no, token = token_line[0], token_line[1] # extract token
                    if not ('-' in line_no):
                        line.append(token_line[1])  
                    n = re.findall(r'\\n', token_line[9])
                    if n:
                        lines.append(' '.join(line) + '\n'*len(n))
                        line = []
                        
        out_file = '.'.join(file.split('.')[:-1]) + ending
        out_path = os.path.join(output_dir, out_file)
        with open(out_path, 'w') as f:
            print(f' \u2b91  writing tokens ({len(lines)} lines) to:', out_path)
            f.writelines(lines)
        print()

if __name__ == '__main__':
    tokenize(sys.argv[1])
