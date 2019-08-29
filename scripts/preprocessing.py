import sys, os, ntpath, re
# UDPipe tokenize.py
from .helpers import default_by_lang, create_dir, udpipe_model_to_code, save_dict, get_dict
from .config import *
from .utils import Batch

def add_fast_text_n(input_file, ending=True, assertion=True):
    input_path = os.path.abspath(input_file)
    input_dir  = os.path.dirname(input_path)
    filename   = os.path.basename(input_path)

    dict_path  = os.path.join(input_dir, 'empty.dict')
    with open(dict_path) as f:
        empty_dict = eval(f.read())
    with open(input_path) as f:
        fast_text_lines = f.readlines()

    if ending:
        filename = filename.rsplit('.', 1)[0]
    for e_id in empty_dict[filename]:
        if assertion:
            assert fast_text_lines[e_id] != '\n', f'Error line: {e_id}\n{input_path} already contains "\\n"!'
        fast_text_lines.insert(e_id, '\n')
        assertion = False
    with open(input_path, 'w') as f:
        f.writelines(fast_text_lines)


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

def resublinks(input_file, strict=True):
    input_path = os.path.abspath(input_file)
    filename   = input_path.basename(input_path)

    dict_path = os.path.join(os.path.dirname(input_path), 'link.dict')
    dict_data = get_dict(dict_path)
    link_dict = dict_data[filename]
    with open(input_file) as f:
        lines = f.readlines()
    for SUB_TOKEN in link_dict:
        i = int(SUB_TOKEN.split('_')[3])
        lines[i] = lines[i].replace(SUB_TOKEN, link_dict[SUB_TOKEN])


def sublinks(input_file):
    input_path = os.path.abspath(input_file)
    with open(input_path) as f:
        lines = f.readlines()

    link_dict = {}
    with open(input_path, 'w') as f:
        for i, line in enumerate(lines):
            if re.search(r'\w+\.[a-z]{2,15}\s*\n', line):
                mail_reg = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)(\s*\n)'
                link_reg = r'((http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[A-Za-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?)(:?\s*\n)'

                mail = re.findall(mail_reg, line)
                link = re.findall(link_reg, line)
                if mail:
                    SUB_TOKEN = fr'__MAIL_{i:04}__'
                    line = re.sub(mail_reg, SUB_TOKEN+r'\2', line)
                    link_dict[SUB_TOKEN] = mail[0][0]
                elif link:
                    SUB_TOKEN = fr'__LINK_{i:04}__'
                    line = re.sub(link_reg, SUB_TOKEN+r'\6', line)
                    link_dict[SUB_TOKEN] = link[0][0]
                else:
                    print('**** WARNING: Uncatched link ****')
                    print(line)
                    SUB_TOKEN = None
                    print('**** Uncatched link end ****')
                print(link_dict.get(SUB_TOKEN), '-->', SUB_TOKEN, line)
            f.write(line)
        dict_path = os.path.join(os.path.dirname(input_path), 'link.dict')
        dict_data = {os.path.basename(input_path): link_dict}
        save_dict(dict_path=dict_path, dict_data=dict_data)


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