import sys, os, ntpath, re
# UDPipe tokenize.py
from .helpers import default_by_lang, create_dir, udpipe_model_to_code, save_dict, get_dict, get_corpus_files, get_dict, get_files
from .config import *
from .utils import Batch

def add_fast_text_n(input_path, ending=True, assertion=True):
    input_path = os.path.abspath(input_path)
    if os.path.isdir(input_path):
        files = get_files(input_path, allowed_endings=['.rev', '.fwd'])
        if not files:
            print('No valid files found in:', input_path)
        for filename in files:
            try:
                add_fast_text_n(os.path.join(input_path, filename))
            except AssertionError as e:
                print(e)
                print(f' .. "{filename}" omitted.')
            print()
        return

    input_path = os.path.abspath(input_path)
    input_dir  = os.path.dirname(input_path)
    filename   = os.path.basename(input_path)
    print('Processing:', input_path, '..')

    dict_path  = os.path.abspath(os.path.join(input_dir, '..', 'merged', 'empty.dict'))
    empty_dict = get_dict(dict_path, verbose=False)
    with open(input_path) as f:
        lines = f.readlines()
    if ending:
        filename = filename.rsplit('.', 1)[0]
    assert len(lines) != empty_dict[filename+'.no_lines'], 'No lines added - already has correct number of lines.'
    for e_id in empty_dict[filename]:
        lines.insert(e_id, '\n')
    assert len(lines) == empty_dict[filename+'.no_lines'], f'Something is wrong. Got {len(lines)} lines but expected {empty_dict[filename+".no_lines"]} lines.'
    with open(input_path, 'w') as f:
        f.writelines(lines)
    print('Empty lines successfully added.')


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
    if os.path.isdir(input_path):
        files = get_corpus_files(input_path)
        for file in files:
            try:
                resublinks(file)
                print()
            except AssertionError as e:
                print(e)
                print(f' .. "{file}" omitted.')
                continue
            except KeyError as e:
                print(e)
                print(f' .. "{file}" omitted.')
                continue
        return
    filename   = os.path.basename(input_path)

    dict_path = os.path.join(os.path.dirname(input_path), 'link.dict')
    dict_data = get_dict(dict_path)
    link_dict = dict_data[filename]
    with open(input_path) as f:
        lines = f.readlines()
    for SUB_TOKEN in link_dict:
        i = int(SUB_TOKEN.split('_')[3])
        assert SUB_TOKEN in lines[i], f'Coud not fould token "{SUB_TOKEN}" at line {i}'
        lines[i] = lines[i].replace(SUB_TOKEN, link_dict[SUB_TOKEN])
        print(f'{i: 9} {SUB_TOKEN}   --->   {link_dict[SUB_TOKEN]}')
    with open(input_path, 'w') as f:
        f.writelines(lines)
        print(f'{len(link_dict)} placeholders were substituted by links.')
        print('Changes saved to:', input_path)


def sublinks(input_path, i_prec=7):
    input_path = os.path.abspath(input_path)
    if os.path.isdir(input_path):
        files = get_corpus_files(input_path)
        for file in files:
            sublinks(file)
            print()
        return
    filename   = os.path.basename(input_path)

    with open(input_path) as f:
        lines = f.readlines()

    link_dict = {}
    mail_reg = '([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)(\s*\n|$)'
    link_reg = r'((http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[A-Za-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?)(:?\s*\n|$)'
    dotname_reg = r'([A-Z]\w+\.[A-Z]\w+)(\s*\n|$)'
    with open(input_path, 'w') as f:
        print('Reading:', input_path)
        for i, line in enumerate(lines):
            if re.search(r'\w+\.[A-Za-z]{2,15}\s*(\n)', line) or re.search(dotname_reg, line):


                #re.sub(r'([A-Z]\w+\.[A-Z]\w+)(\s*\n)', 'test'+r'\2', l)
                mail = re.findall(mail_reg, line)
                link = re.findall(link_reg, line)
                dot_name = re.findall(dotname_reg, line)
                print(mail)
                print(link)
                print(dot_name)
                if mail:
                    SUB_TOKEN = fr'__MAIL_{i:09}__'
                    line = re.sub(mail_reg, SUB_TOKEN+r'\2', line)
                    link_dict[SUB_TOKEN] = mail[0][0]
                elif dot_name:
                    SUB_TOKEN = fr'__DOT_NAME__{i:09}__'
                    line = re.sub(dotname_reg, SUB_TOKEN+r'\2', line)
                    link_dict[SUB_TOKEN] = dot_name[0][0]
                elif link:
                    SUB_TOKEN = fr'__LINK_{i:09}__'
                    line = re.sub(link_reg, SUB_TOKEN+r'\6', line)
                    link_dict[SUB_TOKEN] = link[0][0]
                else:
                    print('**** WARNING: Uncatched link ****')
                    print(line)
                    SUB_TOKEN = None
                    print('**** Uncatched link end ****')
                print(f'{i: 9} {SUB_TOKEN}   <---   {link_dict[SUB_TOKEN]}')
            f.write(line)
        print(f'{len(link_dict)} links were substituted by placeholders.')
        dict_path = os.path.join(os.path.dirname(input_path), 'link.dict')
        dict_data = {filename: link_dict}
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


def news_commentary_v14(download_dir='.'):
    print('Saving corpus "news_commentary_v14" to:', download_dir)
    os.system(f'sh scripts/shell_scripts/download_news_commentary.sh {download_dir}')