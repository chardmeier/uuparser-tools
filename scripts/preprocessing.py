import sys, os, ntpath, re
# UDPipe tokenize.py
from .helpers import default_by_lang, create_dir, udpipe_model_to_code
from .config import *
from .utils import Batch

def replace_chars_file(filepath):
    filepath = os.path.abspath(filepath)
    replace_pairs = [('\u2028', ' '), ('\x85', '')]
    with open(filepath) as f:
        data = f.read()
        for pair in replace_pairs:
            data = data.replace(*pair)
    with open(filepath, 'w') as f:
            f.write(data)
    print('Replaced:', replace_pairs)
    print('.. in', filepath)


def replace_chars_dir(target_dir):
    # Script replaces characters in all files in the respective target directory
    assert os.path.isdir(target_dir)
    target_dir = os.path.abspath(target_dir)
    replace_pairs = [('\u2028', ' '), ('\x85', '')]

    files = os.listdir(target_dir)
    files = list(filter(lambda x: not os.path.isdir(os.path.join(target_dir, x)), files))
    print(f'Processing directory: {target_dir} ..')
    for file in files:
        print(f' - File: {file}')
        file = os.path.join(target_dir, file)
        with open(file) as f:
            data = f.read()
            for pair in replace_pairs:
                data = data.replace(*pair)

        with open(file, 'w') as f:
            f.write(data)
    print('Replaced:', replace_pairs)
    print('For files in:', target_dir)


def remove_n(input_file):
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

def sublinks(input_file):
    input_path = os.path.abspath(input_file)
    with open(input_path) as f:
        lines = f.readlines()
    with open(input_path, 'w') as f:
        for i, line in enumerate(lines):
            if re.search(r'\w+\.[a-z]{2, 15}+\s*\n', line):
                new_line = re.sub(r'(\w+)\.(\w+\s+)', r'\1\\.\2', line)
                print(i, line, '-->', new_line)
                line = new_line
            f.write(line)

def add_nl2x(input_file):
    input_path = os.path.abspath(input_file)
    print(f'Adding \\n to every line in: {input_path}')
    with open(input_path) as i:
        lines = i.readlines()
        print(f'Reading {len(lines)} lines.')
    with open(input_path, 'w') as o:
        lines = list(map(lambda l: l + '\n', lines))
        print(f'Writing {len(lines)*2} lines.')
        o.writelines(lines)

def del_nl2x(input_file):
    input_path = os.path.abspath(input_file)
    print(f'Adding \\n to every line in: {input_path}')
    with open(input_path) as i:
        lines = i.readlines()
        print(f'Reading {len(lines)} lines.')
    with open(input_path, 'w') as o:
        for j in range(len(lines)):
            if j % 2 == 1:
                lines[j] = lines[j][:-1]
        print(f'Writing {len(lines)//2} lines.')
        o.writelines(lines)


def split(input_file, chunksize, conll=False, nl2x=False):
    print('nl2x', nl2x)
    assert os.path.isfile(input_file), f'File "{input_file}" not found!'
    input_path = os.path.abspath(input_file)
    print(f'Splitting file: {input_path}')
    input_filename = ntpath.basename(input_path)
    input_dir = os.path.dirname(input_path)

    with open(input_path) as f:
        counter = 0
        current_part = 0
        current_part_lines = []
        part_list = []
        
        
        for line in f:            
            if nl2x:
                current_part_lines.append(line+'\n')
            else:
                current_part_lines.append(line)

            if conll and line.startswith('#'):
                counter += 1
            else:
                counter += 1
            
            if counter >= chunksize and line == '\n': ### Looking for empty line
                path = os.path.join(input_dir, f'PART_{current_part:02d}___{input_filename}') # Writing Parts
                part_list.append(path)
                print(f'Writing ({len(current_part_lines)}):', path)  
                with open(path, 'w') as p:
                    p.writelines(current_part_lines)
                    
                    counter = 0
                    current_part += 1
                    current_part_lines = []
        path = os.path.join(input_dir, f'PART_{current_part:02d}___{input_filename}')        # Writing last Part
        part_list.append(path)
        print(f'Writing ({len(current_part_lines)}):', path)           
        with open(path, 'w') as p: 
            p.writelines(current_part_lines)
        path = os.path.join(input_dir, f'{input_filename}.parts')
        with open(path, 'w') as log:
            log.write(repr(part_list))
            
        return part_list