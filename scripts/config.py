import os

PROJECT=    os.environ.get('PROJECT')
PARSER=     os.path.join(PROJECT, "uuparser/barchybrid")
BATCHFILES= os.path.join(PROJECT, "batchfiles")
LOGS=       os.path.join(PROJECT, "logfiles")
DATA=       os.path.join(PROJECT, "data")
MODELS=     os.path.join(PROJECT, "models")
SCRIPTS=    os.path.join(PROJECT, "scripts")

EFLOMAL=    os.path.abspath(os.path.expanduser('~/software/eflomal/'))

SOURCE_PATH = os.path.join(PROJECT, 'pn.env')

NAME_PARSER="UUParser"
NAME_TOKENIZER="UDPipe"

TREEBANKS = os.path.join(DATA, 'ud-treebanks-v2.4')


parser_default_mappings = {'de':'de_gsd', 'en':'en_ewt', 'cs':'cs_pdt', 'fr':'fr_gsd', 'sv':'sv_talbanken'}


from .mappings import code2lang


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
# add endings .tokens, .fast_text