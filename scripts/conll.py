import sys, os, ntpath, re
# UDPipe tokenize.py
from .helpers import default_by_lang, create_dir, udpipe_model_to_code
from .config import *
d = parser_default_mappings
from .utils import Batch

def parse(arg1, model_path=None):
    # arg1: path to file that will be tokenized/tagged
    # input file is expected to end with the respective language for example: abc.xy.en
    input_path = os.path.abspath(arg1)
    input_file = ntpath.basename(input_path)

    print(f'Reading file: {input_path}')
    input_dir = os.path.dirname(input_path)
    output_dir  = os.path.join(input_dir, 'parsed')
    create_dir(output_dir)
    print('Output directory:', output_dir)

    
    lang = re.findall(r'.*\.[a-z]{2}-[a-z]{2}\.([a-z]{2})\.?[a-zA-Z]*', input_file)[0]
    model_path = f"{MODELS}/UUParser/{d[lang]}/"

    log_path = f"{LOGS}/parser"
    create_dir(log_path)

    batch = Batch(name=f'parse_{lang}', memory='60GB', log_path=log_path)
    batch.parse(model_path=model_path, input_path=input_path, output_dir=output_dir)
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

    assert input_filename.endswith('.conll')
    output_file  = '.'.join(input_filename.split('.')[:-1] + ['txt']) 
    output_path  = os.path.join(output_dir, output_file)
    print(f'Tokens will be saved to:\n'+output_path)

    
    with open(input_path) as f:
        print('Opening file:\n'+input_path)
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
    extract_tokens(sys.argv[1])
