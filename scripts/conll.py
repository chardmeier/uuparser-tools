import sys, os, ntpath, re, pprint
# UDPipe tokenize.py
from .helpers import default_by_lang, create_dir, udpipe_model_to_code, get_split_files
from .config import *
d = parser_default_mappings
from .utils import Batch

class Counter:
    def __init__(self, i=0, line_i=0):
        self.i = i
        self.line_i = line_i
        
    def count_line(self):
        self.line_i += 1
    
    def next_i(self):
        self.i += 1
        return str(self.i)
    
    def process_line(self, line):
        self.count_line()
        if line.startswith('# sent_id = '):
            return f'# sent_id = {self.next_i()}\n'
        elif line.startswith('# newdoc id = '):
            return ''
        else:
            return line


def merge_conll(input_dir, match_string, output_name=None):
    input_dir = os.path.abspath(input_dir)

    part_files = get_split_files(input_dir, match_string)

    if not output_name:
        output_name = part_files[0].split('_'*3)[-1] + '.conll'
        
    output_path = os.path.join(input_dir, output_name)
    c = Counter()
    print('\nMerged output will be saved to:')
    print(output_path)
    with open(output_path, 'w') as out:
        out.write(f"# newdoc id = {output_name}\n")
        for i, file in enumerate(part_files):
            print(f'.. processing (starting at line: {c.line_i}): {file} ')
            file_path = os.path.join(input_dir, file)
            with open(file_path) as f:
                for line in f:
                    out.write(c.process_line(line))

def train_parser(code):
    log_path = f"{LOGS}/{PARSER_NAME}"
    create_dir(log_path)
    batch = Batch(name=f'tp_{code}', memory='60GB', log_path=log_path)
    batch.train_parser(code)
    batch.submit()

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
    model_path = f"{MODELS}/{PARSER_NAME}/{d[lang]}/" # ADD JOIN

    log_path = f"{LOGS}/{PARSER_NAME}"
    create_dir(log_path)

    batch = Batch(name=f'parse_{lang}', memory='60GB', log_path=log_path)
    batch.parse(model_path=model_path, input_path=input_path, output_dir=output_dir)
    batch.submit()

def parse_split(input_dir, match_string):

    files = os.listdir(input_dir)
    part_files = list(filter(lambda x: re.match(fr'PART_\d+___.*{match_string}.*\.conll', x), files))
    print('Found parts:')
    pprint.pprint(part_files)
    for file in part_files:
        parse(os.path.join(input_dir, file))
        print()

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



class Counter:
    def __init__(self, i=0):
        self.i = i
    
    def next_i(self):
        self.i += 1
        return str(self.i)
    
    def process_line(self, line):
        if line.startswith('# sent_id = '):
            return f'# sent_id = {self.next_i()}\n'
        elif line.startswith('# newdoc id = '):
            return ''
        else:
            return line


def merge_conll(input_dir, match_string, output_name=None):
    input_dir = os.path.abspath(input_dir)
    file_list = os.listdir(input_dir)
    part_files = list(filter(lambda x: re.match(fr'PART_\d+___.*{match_string}.*\.conll', x), file_list))
    part_files.sort(key=lambda x: int(x.split('_')[1]))
    print('Merging files:')
    pprint.pprint(part_files)
    if not output_name:
        output_name = part_files[0].split('_'*3)[-1] + '.conll'
        
    output_path = os.path.join(input_dir, output_name)
    c = Counter()
    print('\nSaving merged output to:')
    print(output_path)
    with open(output_path, 'w') as out:
        out.write(f"# newdoc id = {output_name}\n")
        line_i = 1
        for i, file in enumerate(part_files):
            print(f'.. processing: {file}')
            file_path = os.path.join(input_dir, file)
            with open(file_path) as f:
                for line in f:
                    out.write(c.process_line(line))
        


if __name__ == '__main__':
    extract_tokens(sys.argv[1])
