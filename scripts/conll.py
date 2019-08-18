import sys, os, re, pprint
# UDPipe tokenize.py
from .helpers import *
from .config import *
d = parser_default_mappings
from .utils import Batch

def remove_added_n(input_file):
    """Removes added \n from file. Note: File will be overwritten!"""
    input_path = os.path.abspath(input_file)
    print(f'Removing added newlines in: {input_path}')
    with open(input_path) as f:
        text = f.read()
    r = r"""SpacesAfter=\\n\\n\n\n# newpar"""
    n = r"""SpacesAfter=\\n\n"""
    text = re.sub(r, n, text)
    r = r"SpacesAfter=\\n\\n\\n\\n"
    n = r"SpacesAfter=\\n\\n"
    text = re.sub(r, n, text)

    with open(input_path, 'w') as f:
        f.write(text)

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


def merge_conll(input_dir, match_string, output_name=None, nl2x=True):
    input_dir = os.path.abspath(input_dir)

    part_files = get_split_files(input_dir, match_string)

    if not output_name:
        output_name = part_files[0].split('_'*3)[-1]
        
    output_path = os.path.join(input_dir, output_name)
    c = Counter()
    print('\nMerged output will be saved to:')
    print(output_path)
    with open(output_path, 'w') as out:
        out.write(f"# newdoc id = {output_name}\n")
        for i, file in enumerate(part_files):
            print(f'.. processing (starting at sent {c.i+1}: {c.line_i}): {file} ')
            file_path = os.path.join(input_dir, file)
            with open(file_path) as f:
                for line in f:
                    out.write(c.process_line(line))
    if nl2x:
        remove_added_n(output_path)

def train_parser(code):
    batch = Batch(name=f'tp_{code}', memory='60GB', log_dir=PARSER_NAME)
    batch.train_parser(code)
    batch.submit()

def parse(arg1, model_path=None):
    # arg1: path to file that will be tokenized/tagged
    # input file is expected to end with the respective language for example: abc.xy.en
    input_path = os.path.abspath(arg1)
    input_file = os.path.basename(input_path)

    print(f'Reading file: {input_path}')
    input_dir, output_dir = create_same_level_output_dir(os.path.dirname(input_path), 'parsed')
    # input_dir expected to be .conll/

    
    lang = re.findall(r'.*\.[a-z]{2}-[a-z]{2}\.([a-z]{2})\.?[a-zA-Z]*', input_file)[0]
    model_path = f"{MODELS}/{PARSER_NAME}/{d[lang]}/" # ADD JOIN

    batch = Batch(name=f'parse_{lang}', memory='60GB', log_dir=PARSER_NAME)
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

def chr_format_file(input_file, output_file, verbose=True):
    input_file = os.path.abspath(input_file)
    output_file = os.path.abspath(output_file)
    with open(input_file) as f:
        if verbose:
            print('Reading file:', input_file)
        doc_id = 1
        current_sent = []
        doc_sents    = []
        
        out_lines = []
        for line in f:
            #print(current_sent, doc_sents)
            if line.startswith('# newpar'):
                if doc_sents:
                    print_doc_id = str(doc_id)
                    doc_id += 1
                    for i, sent in enumerate(doc_sents):
                        doc_line = str(i+1)
                        out_line = '\t'.join((print_doc_id, doc_line, sent)) + '\n'
                        out_lines.append(out_line)
                        print_doc_id = ''
                    out_lines.append('\n')
                current_sent = []
                doc_sents    = []
            elif line.startswith('# sent_id'):
                if current_sent:
                    doc_sents.append(' '.join(current_sent))
                    current_sent = []
            elif line.startswith('#') or line == '\n':
                continue
            else:
                token = line.split()[1]
                current_sent.append(token)
    with open(output_file, 'w') as o:
        if verbose:
            print(f' \u2b91  writing chr-format output to:', output_file)
            print()
        o.writelines(out_lines)
                
def chr_format_dir(input_dir, verbose=True):
    print('Convert .conll -> chr-format')
    input_dir, output_dir = create_same_level_output_dir(input_dir, 'chr_format')
    
    files = get_conlls(input_dir)
    for file in files:
        input_file  = os.path.join(input_dir, file)
        output_file = os.path.join(output_dir, file[:-5] + 'chr')
        chr_format_file(input_file, output_file, verbose)

def extract_tokens(input_dir, nl2x=False):
    #main_dir  = os.path.abspath(sys.argv[1])

    # set ending of output files  (dot (.) must be included !):
    ending = '' # '.token'

    input_dir, output_dir = create_same_level_output_dir(input_dir, 'tokens')
    files = get_conlls(input_dir)

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
    extract_tokens(sys.argv[1])
