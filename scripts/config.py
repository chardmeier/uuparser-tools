import os

DATA   = os.environ.get('DATA')
MODELS = os.environ.get('MODELS')
PROJECT = os.environ.get('PROJECT')
BATCHFILES = os.environ.get('BATCHFILES')
LOGS = os.environ.get('LOGS')
SCRIPTS = os.environ.get('SCRIPTS')
PARSER = os.environ.get('PARSER')

TOKENIZER_NAME = os.environ.get('NAME_TOKENIZER')


with open(os.path.join(SCRIPTS, 'code2lang.dict')) as f:
    code2lang = eval(f.read())

"""MODELS = "abs/models"
DATA = 'abc/data'
PARSER_NAME = 'UUParser'
PARSER = "abs/uuparser/barchybrid"
LOGS = "abs/logfiles"""