import sys, os, re, pprint
# UDPipe tokenize.py
from .helpers import *
from .config import *
d = parser_default_mappings
from .utils import Batch

class Counter:
    """ Helpers class for merging conll files"""
    def __init__(self, i=0, line_i=0):
        self.i = i
        self.line_i = line_i
        self.nl2x_n = 0
        self.new_n  = 0
        
    def count_line(self):
        """ Keeps track of current line id """
        self.line_i += 1
    
    def next_i(self):
        self.i += 1
        return str(self.i)
    
    def process_line(self, line):
        """ Processed ine and adapts document and sent id"""
        self.count_line()
        if line.startswith('# sent_id = '):
            return f'# sent_id = {self.next_i()}\n'
        elif line.startswith('# newdoc id = '):
            return ''
        else:
            return line

def merge_conll_nl2x(input_dir, match_string, output_name=None, nl2x=True):
    """
    Merges split .conll files. With newlines added that will be removed during merging
    args:
        input_dir (string): path to input directory
        match_string (string): string that matches all split files for example 'de-en.de'
        output_name (string): optional custom filename for output
        nl2x (bool): If set True added \\n will be removed from file during merging / not tested thoroughly, for nl2x=False better use merge_conll()
    """
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

def merge_conll(input_dir, match_string, output_name=None):
    """
    Merges split .conll files. Without new lines added.
    args:
        input_dir (string): path to input directory
        match_string (string): string that matches all split files for example 'de-en.de'
        output_name (string): optional custom filename for output
    """
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

def train_parser(code, args=None):
    """ 
    Submits training job on UUParser on given treebank code
    args:
        code (string): language code of UD-treebank
        args (None or argparser.args): additional arguments to modify parameters such es memory, timelimit or partition to run on
    """
    batch = Batch(name=f'tp_{code}', log_dir=NAME_PARSER, args=args)
    batch.train_parser(code)
    batch.submit()

def parse(arg1, model_path=None, args=None):
    """
    Creates a parsing job for given intputs. Language detection will be done automatically.
    Input file is expected to hold the following format for language detection: '.*\.[a-z]{2}-[a-z]{2}\.([a-z]{2})\.?[a-zA-Z]*'
    args:
        arg1 (string): path to file that will be tokenized/tagged
    """
    # 
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
    """
    Submits parsing jobs on splitted .conll files
    args:
        input_dir (string): path to input directory
        match_string (string): string that matches all split files for example 'de-en.de'
    """
    files = os.listdir(input_dir)
    part_files = list(filter(lambda x: re.match(fr'PART_\d+___.*{match_string}.*\.conll', x), files))
    print('Found parts:')
    pprint.pprint(part_files)
    for file in part_files:
        parse(os.path.join(input_dir, file))
        print()


import linecache, re
class CoNLLReader:
    def __init__(self, filepath):
        print('Reading file:', filepath)
        self.filepath = filepath
        with open(filepath) as f:
            self.__len = sum(1 for line in f)
            
        self._i = 0
        
    def write_chr(self, save_path):
        num_line_ids = 0
        written_lines = 0
        with open(save_path, 'w') as f:
            for doc in self.docs:
                lines = doc.get_chr()
                num_line_ids += doc.num_line_ids
                written_lines += len(lines)
                f.write('\n'.join(lines))
                f.write('\n')
        print(f'{num_line_ids} line ids written.')
        print(f' \u2b91  writing chr-format output ({written_lines} overall lines) to:', save_path)
        print()
            
    @property    
    def docs(self):
        sent_list = []
        doc_id = 0
        for i, sent in enumerate(self.sents):
            if sent.newpar and sent_list:
                doc_sents, sent_list = sent_list, []
                doc_id += 1
                yield Doc(doc_sents, doc_id=doc_id)
            sent_list.append(sent)
        doc_id += 1
        yield Doc(sent_list, doc_id=doc_id)
        
    @property
    def sents(self):
        while True:
            sent = self.next_sent()
            if sent:
                yield sent
            else:
                break
        
    def get_line(self, i):
        return linecache.getline(self.filepath, i)
    
    def next_line(self):
        self._i += 1
        return self.get_line(self._i)
    
    def next_sent(self):
        lines = []
        current_line = self.next_line()
        while current_line and current_line != '\n':
            lines.append(current_line)
            current_line = self.next_line()
        if lines:
            return Sent(lines)
        
class Doc:
    def __init__(self, sents, doc_id):
        self.sents = sents
        self.doc_id = doc_id
        self.num_line_ids = 0
        
    def create_chr_line(self, text, sent_id, doc_id=''):
        return '\t'.join(doc_id, sent_id, doc_id)
        
    def get_chr(self):
        doc_id = str(self.doc_id)
        n_id = 1
        output_lines = []
        for sent in self.sents:
            for i in range(sent.pre_n):
                output_lines.append('\t'.join((doc_id, str(n_id), '')))
                self.num_line_ids += 1
                n_id += 1
                doc_id = ''
            write_n_id = ''
            if sent.post_n:
                write_n_id = str(n_id)
                self.num_line_ids += 1
                n_id += 1
            output_lines.append('\t'.join((doc_id, write_n_id, str(sent))))
            doc_id   = ''
            for i in range(max(sent.post_n-1, 0)):
                output_lines.append('\t'.join((doc_id, str(n_id), '')))
                self.num_line_ids += 1
                n_id += 1
                doc_id = ''
        return (output_lines)
                
        
    
    
class Sent:
    def __init__(self, lines, start_line=None):
        
        self.newdoc  = None
        self.newpar  = False
        self.sent_id = None
        
        self.start_line = start_line
        while lines and lines[0].startswith('#'):
            info_line = lines.pop(0)
            if '# newpar' in info_line:
                self.newpar = True
            elif '# newdoc' in info_line:
                self.newdoc = info_line.split(' = ')[-1]
            elif '# sent_id' in info_line:
                self.sent_id = int(info_line.split(' = ')[-1])
        self.lines = list(map(lambda l: l.split('\t'), lines))
        self.handle_minus()
        self.pre_n  = 0
        self.post_n = 0
        self.mid_n  = 0
        self.extract_spaces()            
        
    def extract_spaces(self):
        for i, line in enumerate(self.lines):
            space_segment = line[9]
            n = len(re.findall(r'\\n', space_segment))
            if 'SpacesBefore' in space_segment:
                if i == 0:
                    self.pre_n += n
                else:
                    self.mid_n += n
                    if n:
                        print('Sent_id:', self.sent_id, f'Found \\n in within sentence:', line[0], line[1], space_segment)
            else:
                if i == len(self)-1:
                    self.post_n += n
                else:
                    self.mid_n += n   
                    if n:
                        print('Sent_id:', self.sent_id, f'Found \\n in within sentence:', line[0], line[1], space_segment)

    def handle_minus(self):
        d = {}
        i = 0
        while i < len(self):
            if '-' in self.lines[i][0]:
                d[int(self.lines[i][0].split('-')[-1])] = self.lines[i][9]
                self.lines.pop(i)
            else:
                i += 1
        for key in d:
            self.lines[key-1][9] = d[key]

        
    def __len__(self):
        return len(self.lines)
    
    def __str__(self):
        return repr(self)
        
    def __repr__(self):
        return ' '.join(map(lambda l: l[1], self.lines))
    
    

#cnlr = CoNLLReader('news-commentary-v14.de-en.en.conll')
#cnlr.write_chr('test_out_en.chr')

def chr_format_file(input_file, output_file, verbose=True, empty_line=''):
    """
    Creates .chr format file form .conll file
    args:
        input_file (string): path to input file
        output_file (string): path where output will be saved to
        verbose (bool): controlls print outs
    """
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
        count_line_ids = 0
        for conll_line_id, line in enumerate(f):
            #print(current_sent, doc_sents)
            if line.startswith('# newpar'): # initalize new document
                if current_sent:            # if there is a # newpar after a sentence it must be still written to old doc
                    doc_sents.append(' '.join(current_sent))
                    current_sent = []
                    n_in_sent.append((True in n_in_token))  # checking if a token in sent is followed by \n
                    n_in_token = []
                    for i in range(n-1):
                        doc_sents.append(empty_line)
                        n_in_sent.append(True)
                    n = 0
                    pre_n = 0
                if doc_sents: 
                    print_doc_id = str(doc_id)   # set doc_id to write at first doc line
                    doc_id += 1                  # add doc id
                    line_id = 1
                    print_next_line_id = str(line_id)*True
                    for i, sent in enumerate(doc_sents):    # write all doc sents
                        line_id += n_in_sent[i]
                        count_line_ids += int(bool(print_next_line_id))
                        out_line = '\t'.join((print_doc_id, print_next_line_id, sent)) + '\n'
                        if print_next_line_id == '\\n':
                            print(line_id)
                            print(out_line)
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
                    for i in range(n-1):
                        doc_sents.append(empty_line)
                        n_in_sent.append(True)
                    for i in range(pre_n):
                        doc_sents = [empty_line] + doc_sents
                        n_in_sent = [True] + n_in_sent
                    n = 0
                    pre_n = 0
            elif line.startswith('#') or line == '\n':
                assert line.startswith('# text') or line.startswith('# newdoc') or line == '\n', f'Got: {line}'
                continue
            else:
                line_split = line.split()
                line_no, token = line_split[0], line_split[1]
                if not ('-' in line_no):
                    current_sent.append(token)
                    n_in_token.append(('\\n' in line_split[9])) # checks for \n at the end of sent (\n should not appear within the sentence)
                    n = len(re.findall(r'\\n', line_split[9]))
                    pre_n = 0
                    if n and 'SpacesBefore' in line_split[9]:
                        pre_n = n
                        n = 0
                        assert line_no == 1, f'SpacesBefore should only occur at the beginning of a sentence got sentence line {line_no} in {conll_line_id}'
                        del n_in_token[-1]


        if current_sent:            # if there is a # newpar after a sentence it must be still written to old doc
            doc_sents.append(' '.join(current_sent))
            current_sent = []
            n_in_sent.append((True in n_in_token))
            n_in_token = []
            for i in range(n-1):
                doc_sents.append(empty_line)
                n_in_sent.append(True)
            n = 0
            pre_n = 0
            if doc_sents: 
                print_doc_id = str(doc_id)   # set doc_id to write at first doc line
                doc_id += 1                  # add doc id
                line_id = 1
                print_next_line_id = str(line_id)*True
                for i, sent in enumerate(doc_sents):    # write all doc sents
                    line_id += n_in_sent[i]
                    count_line_ids += int(bool(print_next_line_id))
                    out_line = '\t'.join((print_doc_id, print_next_line_id, sent)) + '\n'
                    out_lines.append(out_line)
                    print_doc_id = ''
                    print_next_line_id = str(line_id)*n_in_sent[i]
    print(f'Found {count_insent_n} sentences that contain multiple "\\n".')
    print(f'{count_line_ids} line ids written.')
    with open(output_file, 'w') as o:
        if verbose:
            print(f' \u2b91  writing chr-format output ({len(out_lines)} overall lines) to:', output_file)
            print()
        o.writelines(out_lines)
                
def chr_format_dir(input_dir, verbose=True):
    """
        Converts .conll files in given directory to .chr format
        args:
            input_dir (string): path to directory
            verbose (bool): controlls print outs
    """
    print('Convert .conll -> chr-format')
    input_dir, output_dir = create_same_level_output_dir(input_dir, 'chr_format')
    
    files = get_conlls(input_dir)
    for file in files:
        input_file  = os.path.join(input_dir, file)
        output_file = os.path.join(output_dir, file[:-5] + 'chr')
        cnlr = CoNLLReader(input_file)
        cnlr.write_chr(output_file)

class PlaceholderManager:
    """ 
    Helper class for re-inserting links using resublinks.
    Keeps track of that all links will be replaced correctly. Provides some fualty checks
    """
    def __init__(self, link_dict):
        """
        args:
            link_dict (dict): dictionary containing placeholder:link mappings
        """
        self.link_dict = link_dict
        self.SUB_TOKENS = list(link_dict.keys())
        self.SUB_TOKENS.sort(key=lambda SUB_TOKEN: int(SUB_TOKEN.split('_')[3]))
        self.counter = [0]*len(self.SUB_TOKENS)
        self.i = 0
        self.line_id = -1
        self.first_match = None
        
    def current(self):
        """ Keeps track placeholder oder"""
        if self.i < len(self.SUB_TOKENS):
            return self.SUB_TOKENS[self.i], self.link_dict[self.SUB_TOKENS[self.i]]
        else:
            return False, False
    
    def got_match(self):
        """ Counts number of replacements """
        self.counter[self.i] += 1
        if self.counter[self.i] == 2:
            self.first_match = None
            self.i += 1
            
    def check(self):
        """
        Checks if all every link was exactly inserted two times (Sent Line and Token line)
        """
        if sum(self.counter) != len(self.SUB_TOKENS)*2:
            print('Error: Not all tokens found:')
            print(self.counter)
            print(self.SUB_TOKENS)
            assert sum(self.counter) == len(self.SUB_TOKENS)*2, 'Not all tokens could be found in .conll - changes not saved!'

    def process_line(self, i, line):
        """
        Processes a single line of .conll file and replaces placeholders
        args:
            i (int): line id
            line (string): current line of .conll file
        """
        self.line_id += 1
        placeholder, link = self.current()
        if placeholder and (placeholder in line):
            line = line.replace(placeholder, link)
            print(f'{i: 9} {placeholder}   --->   {link}')
            self.got_match()
        return line

def resublinks(input_file):
    """
    Re-subsitutes Links into conll-files that were replaced by placedholders before tokenization
    Expects dictionary with placeholder / link mappings to be placed in the main corpus directory with name 'link.dict'
    args:
        input_file (string): path to input file or directory
    """
    input_path = os.path.abspath(input_file)
    print(f'Re-subsitute Links in: {input_path}')

    if os.path.isdir(input_path):
        files = get_conlls(input_path)
        files = map(lambda f: os.path.join(os.path.dirname(input_path), file))
        for file in files:
            try:
                resublinks(file)
                print()
            except AssertionError as e:
                print(e)
                print('Ommiting:', file)
                continue
            except KeyError as e:
                print(e)
                print('Ommiting:', file)
                continue
        return
    corpus_file  = os.path.basename(input_path)[:-6] # remove conll
    print('corpus_file', corpus_file)

    dict_path = os.path.abspath(os.path.join(os.path.dirname(input_path), '..', 'link.dict'))
    print('dict_path', dict_path)
    dict_data = get_dict(dict_path)
    link_dict = dict_data[corpus_file]
    if None in link_dict:
        del link_dict[None]
    pm = PlaceholderManager(link_dict)
    with open(input_path) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        lines[i] = pm.process_line(i, line)
    pm.check()
    with open(input_path, 'w') as f:
        f.writelines(lines)
        print(f'{len(link_dict)} placeholders were substituted by links.')
        print('Changes saved to:', input_path)

def extract_tokens(input_arg, nl2x=False):
    """
    Extracts tokens form .conll
    args:
        input_arg (string): can be either path to .conll file or directory containing .conll files
        nl2x        (bool): must be True if \\n where added at the beginning of the pipeline, then additional \\n will be removed
    """
    print('nl2x:', nl2x)
    #main_dir  = os.path.abspath(sys.argv[1])

    # set ending of output files  (dot (.) must be included !):
    ending = '.token' # '.token'
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
