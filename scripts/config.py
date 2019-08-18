import os

DATA   = os.environ.get('DATA')
MODELS = os.environ.get('MODELS')
PROJECT = os.environ.get('PROJECT')
BATCHFILES = os.environ.get('BATCHFILES')
LOGS = os.environ.get('LOGS')
SCRIPTS = os.environ.get('SCRIPTS')
PARSER = os.environ.get('PARSER')

PARSER_NAME = os.environ.get('NAME_PARSER')
TOKENIZER_NAME = os.environ.get('NAME_TOKENIZER')

TREEBANKS = os.path.join(DATA, 'ud-treebanks-v2.4')

parser_default_mappings = {'de':'de_gsd', 'en':'en_ewt', 'cs':'cs_pdt', 'fr':'fr_gsd', 'sv':'sv_talbanken'}


with open(os.path.join(SCRIPTS, 'code2lang.dict')) as f:
    code2lang = eval(f.read())


# ToDO:
# - creating all paths in a more central part of the program
# - integrate custom memory, time and partition
# - integrating merging und alignment in tools.py
# - integrating split merge
# - integrating downloads in tools.py
# - integrating pre-processing in tools.py
#   - replace chards
#   - remove sentences (tables)

# put batch_history_dir in config
# global double_n switch for all operations