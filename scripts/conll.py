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
        self.nl2x_n = 0
        self.new_n  = 0
        
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

"""
import re, sys
l = []
for i, line in enumerate(sys.stdin):
    if ('SpacesAfter=\\n' in line) or ('SpacesAfter=\\s\\n' in line):
        line_seg = line.split('\t')
        nl2x_n = len(re.findall(r'\\n', line_seg[9]))
        first_match = re.search(r'\\n', line_seg[9])
        l.append(nl2x_n)
        print(line_seg[9][:first_match.start()])
        print(nl2x_n, line)
        if nl2x_n == 4:
            print(i)
print(l)
"""

def merge_conll_nl2x(input_dir, match_string, output_name=None, nl2x=True):
    print('nl2x:', nl2x)
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
            print(f'.. processing (starting at sent {c.i+1}): {file} ')
            file_path = os.path.join(input_dir, file)
            with open(file_path) as f:
                lines = []
                remove_next_newpar = False
                for line in f:
                    line = c.process_line(line)
                    if nl2x and ('\\n' in line):
                        line_seg = line.split('\t')

                        nl2x_n = len(re.findall(r'\\n', line_seg[9]))
                        assert nl2x_n % 2 == 0, f'Number of \\n cannot be odd with nl2x activated. Got {nl2x_n} \\n at line {i}'
                        c.nl2x_n += nl2x_n
                        n = nl2x_n // 2
                        c.new_n += n
                        if n < 2:
                            remove_next_newpar = True
                        n_start = re.search(r'\\n', line_seg[9]).start()
                        line_seg[9] = line_seg[9][:n_start] + '\\n'*n + '\n'
                        lines.append('\t'.join(line_seg))
                    elif line:
                        if (not remove_next_newpar) or (not line.startswith('# newpar')):
                            lines.append(line)
                        else:
                            remove_next_newpar = False

                out.writelines(lines)
        print(f'{c.nl2x_n} "\\n" counted in input.')
        print(f'{c.new_n} "\\n" counted in output.')

def merge_conll(input_dir, match_string, output_name=None, nl2x=False):
    print('nl2x:', nl2x)
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
            print(f'.. processing (starting at sent {c.i+1}): {file} ')
            file_path = os.path.join(input_dir, file)
            with open(file_path) as f:
                for line in f:
                    out.write(c.process_line(line))
    if nl2x:
        remove_added_n(output_path)

def train_parser(code, args=None):
    batch = Batch(name=f'tp_{code}', log_dir=NAME_PARSER, args=args)
    batch.train_parser(code)
    batch.submit()

def parse(arg1, model_path=None, args=None):
    # arg1: path to file that will be tokenized/tagged
    # input file is expected to end with the respective language for example: abc.xy.en
    input_path = os.path.abspath(arg1)
    input_file = os.path.basename(input_path)

    print(f'Reading file: {input_path}')
    input_dir, output_dir = create_same_level_output_dir(os.path.dirname(input_path), 'parsed')
    # input_dir expected to be .conll/

    
    lang = re.findall(r'.*\.[a-z]{2}-[a-z]{2}\.([a-z]{2})\.?[a-zA-Z]*', input_file)[0]
    model_path = f"{MODELS}/{NAME_PARSER}/{d[lang]}/" # ADD JOIN

    batch = Batch(name=f'parse_{lang}', log_dir=NAME_PARSER, args=args)
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
        n_in_token   = []
        n_in_sent    = []
        count_insent_n = 0
        out_lines = []
        for conll_line_id, line in enumerate(f):
            #print(current_sent, doc_sents)
            if line.startswith('# newpar'): # initalize new document
                if current_sent:            # if there is a # newpar after a sentence it must be still written to old doc
                    doc_sents.append(' '.join(current_sent))
                    current_sent = []
                    n_in_sent.append((True in n_in_token))  # checking if a token in sent is followed by \n
                    n_in_token = []
                if doc_sents: 
                    print_doc_id = str(doc_id)   # set doc_id to write at first doc line
                    doc_id += 1                  # add doc id
                    line_id = 1
                    print_next_line_id = str(line_id)*True
                    for i, sent in enumerate(doc_sents):    # write all doc sents
                        line_id += n_in_sent[i]
                        out_line = '\t'.join((print_doc_id, print_next_line_id, sent)) + '\n'
                        out_lines.append(out_line)
                        print_doc_id = ''
                        print_next_line_id = str(line_id)*n_in_sent[i]
                    #out_lines.append('\n')
                current_sent = []
                doc_sents    = []
                n_in_sent    = []
            elif line.startswith('# sent_id'):
                if current_sent:
                    doc_sents.append(' '.join(current_sent))
                    current_sent = []
                    if sum(n_in_token) > 1:
                        print('Line:', conll_line_id, f'({sum(n_in_token)})')
                        #print('n_in_token', n_in_token)
                        count_insent_n += 1

                    n_in_sent.append((True in n_in_token))  # checking if a token in sent is followed by \n
                    n_in_token = []
            elif line.startswith('#') or line == '\n':
                assert line.startswith('# text') or line.startswith('# newdoc') or line == '\n', f'Got: {line}'
                continue
            else:
                line_split = line.split()
                token = line_split[1]
                current_sent.append(token)
                n_in_token.append(('\\n' in line_split[9])) # checks for \n at the end of sent (\n should not appear within the sentence)

        if current_sent:            # if there is a # newpar after a sentence it must be still written to old doc
            doc_sents.append(' '.join(current_sent))
            current_sent = []
            n_in_sent.append((True in n_in_token))
            n_in_token = []
            if doc_sents: 
                print_doc_id = str(doc_id)   # set doc_id to write at first doc line
                doc_id += 1                  # add doc id
                line_id = 1
                print_next_line_id = str(line_id)*True
                for i, sent in enumerate(doc_sents):    # write all doc sents
                    line_id += n_in_sent[i]
                    out_line = '\t'.join((print_doc_id, print_next_line_id, sent)) + '\n'
                    out_lines.append(out_line)
                    print_doc_id = ''
                    print_next_line_id = str(line_id)*n_in_sent[i]
    print(f'Found {count_insent_n} sentences that contain multiple "\\n".')
    with open(output_file, 'w') as o:
        if verbose:
            print(f' \u2b91  writing chr-format output ({len(out_lines)}) to:', output_file)
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

def extract_tokens(input_arg, nl2x=False):
    print('nl2x:', nl2x)
    #main_dir  = os.path.abspath(sys.argv[1])

    # set ending of output files  (dot (.) must be included !):
    ending = '' # '.token'
    if os.path.isdir(input_arg):
        input_dir, output_dir = create_same_level_output_dir(input_arg, 'tokens')
        files = get_conlls(input_dir)
    elif os.path.isfile(input_arg):
        input_dir = os.path.dirname(input_arg)
        input_dir, output_dir = create_same_level_output_dir(input_dir, 'tokens')
        assert input_arg.endswith('.conll'), 'Input needs to be .conll-file!'
        files = [os.path.basename(input_arg)]


    for file in files:
        in_path = os.path.join(input_dir, file)
        with open(in_path) as f:
            print('Reading file:', in_path)
            lines = []
            line  = []
            count_n = 0
            for i, token_line in enumerate(f):
                if (not token_line.startswith('#')) and (token_line != '\n'):
                    token_line = token_line.split('\t')
                    line_no, token = token_line[0], token_line[1] # extract token
                    if not ('-' in line_no):         # omit 17-18 in lines am / an dem
                        line.append(token_line[1])  
                    n = len(re.findall(r'\\n', token_line[9]))
                    if n:
                        if nl2x:
                            assert n % 2 == 0, f'Number of \\n cannot be odd with nl2x activated. Got {n} \\n at line {i}'
                            n = n // 2
                        count_n += n
                        lines.append(' '.join(line) + '\n'*n)
                        line = []
                        
        out_file = '.'.join(file.split('.')[:-1]) + ending
        out_path = os.path.join(output_dir, out_file)
        with open(out_path, 'w') as f:
            print(f' \u2b91  writing tokens ({count_n} lines) to:', out_path)
            f.writelines(lines)
        print()


if __name__ == '__main__':
    extract_tokens(sys.argv[1])
