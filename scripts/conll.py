import sys, os, ntpath
# UDPipe tokenize.py
from .helpers import default_by_lang, create_dir, udpipe_model_to_code
from .config import *
from .utils import Batch


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
    print(f'Tokens will be saved to:\n', output_path)

    
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
    extract_tokens(sys.argv[1])
