import sys, os, ntpath
# UDPipe tokenize.py
from .helpers import default_by_lang, create_dir, udpipe_model_to_code
from .config import *
from .utils import Batch

def split(input_file, chunksize, conll=False):
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
            current_part_lines.append(line)
            if conll and line.startswith('#'):
                counter += 1
            else:
                counter += 1
            
            if counter >= chunksize and line == '\n':
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