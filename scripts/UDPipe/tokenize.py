import sys, os, ntpath
# UDPipe tokenize.py
from helpers import default_by_lang, create_dir
from config import *

def tokenize(arg1, model_path=None):
    # arg1: path to file that will be tokenized/tagged
    # input file is expected to end with the respective language for example: abc.xy.en
    input_path = os.path.abspath(arg1)
    input_filename = ntpath.basename(input_path)
    input_dir = os.path.dirname(input_path)
    output_dir  = os.path.join(input_dir, 'conll')
    output_file = os.path.join(output_dir, f'{input_filename}.conll')

    create_dir(output_dir)
    
    lang = input_filename.split('.')[-1]  
    model_path = default_by_lang(lang)  
    """if not model_path:
                    model_path = f"{MODELS}/ud_custom_models"
            
                    if not os.path.isdir(model_path):
                        print('Create directory:', model_path)
                        os.mkdir(model_path)
                        
                    print('Output directory:', output_dir)
            
                    sys.path.append(SCRIPTS)
                    from default_code_mappings import default_mappings as d
                    #d = {'de':'de_gsd', 'en':'en_ewt', 'cs':'cs_pdt', 'fr':'fr_ftb', 'sv':'sv_talbanken'}
                    #cs_pdt.model  de_gsd.model  en_ewt.model  fr_ftb.model sv_talbanken.model
                    model_path = f'{model_path}/{d[lang]}.model'"""

    log_path = f"{LOGS}/UDPipe"
    create_dir(log_path)

    batch_string = f"""#!/bin/sh

    #SBATCH -t 48:00:00
    #SBATCH -n 1
    #SBATCH -J "{lang}_tok"
    #SBATCH --mem-per-cpu=16GB
    #SBATCH --account=nn9447k
    #SBATCH --output={log_path}/tokenize_{lang}-%j.out

    source ~/.bashrc

    module purge
    module load gcc

    srun -t 48:00:00 \
         --mem-per-cpu=16GB \
         --account=nn9447k \
         /projects/nlpl/software/udpipe/latest/bin/udpipe --tokenize --tag {model_path} {input_path} > {output_file}
    """
    batch_path = f'{BATCHFILES}/tokenize.sh'
    with open(batch_path, 'w') as f:
        f.write(batch_string)
        
    os.system(f'sbatch {batch_path}')

if __name__ == '__main__':
    tokenize(sys.argv[1])
