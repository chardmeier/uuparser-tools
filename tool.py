import argparse, os

batch_job_options  = argparse.ArgumentParser(add_help=False)
batch_group = batch_job_options.add_argument_group('Batch Job Script options')
batch_group.add_argument('--mem', '-m', default='60GB', type=str, help='Sets amount of memory allocated for the job. For example "60GB"')
batch_group.add_argument('--duration', '-d', default='96:00:00', type=str, help='Sets the TimeLimit for the job. For example "96:00:00"')
batch_group.add_argument('--name', '-n', type=str, help='Option for setting a manual name for batch job.')
batch_group.add_argument('--partition', type=str, choices=['normal', 'hugemem', 'accel'], default='normal', help='Setting partition for the job to run on (default=normal).')

other_options  = argparse.ArgumentParser(add_help=False)
other_options_group = batch_job_options.add_argument_group('Other options')
other_options_group.add_argument('--split', '-s', action='store_true', help='Activates splitting for large files.')
other_options_group.add_argument('--split_size', type=int, default=150000, help='Sets split size (in lines).')




arg_parser = argparse.ArgumentParser()

subparsers = arg_parser.add_subparsers(title="commands", dest="command", help='Tool options:')

sub_name = 'parser'
uuparser_args = subparsers.add_parser(sub_name, help='Options for UUParser', parents=[batch_job_options])
# use store true, set split size separately 
train_parse = uuparser_args.add_mutually_exclusive_group(required=True)
train_parse.add_argument('--parse', '-p', type=str, help='Expects path to .conll file that will be parsed using UUParser')
train_parse.add_argument('--train', '-t', type=str, help='Trains UUParser on a given treebank, expects treebank language code as input such as "de_gsd"')

sub_name = 'conll'
conll_args = subparsers.add_parser(sub_name, help='Options for .conll files', parents=[batch_job_options])
conll_parse = conll_args.add_mutually_exclusive_group(required=True)
conll_parse.add_argument('--parse', '-p', type=str, nargs='*', metavar=('INPUT', 'MATCH_STRING'),
    help='INPUT musst be a .conll file or a directoy containing split conlls when --split is set. \nMATCH_STRING must be a string that all respective parts share e.g. the original file name like: "europarl-v7.de-en.de"')
conll_parse.add_argument('--extract_tokens', '-e', type=str, help='Expects path to .conll file from that tokens will be extracted.')


sub_name = 'tokenizer'
tokenizer_args = subparsers.add_parser(sub_name, help='Options for UDPipe Tokenizer', parents=[batch_job_options])

train_tokenize = tokenizer_args.add_mutually_exclusive_group(required=True)
train_tokenize.add_argument('--tokenize', type=str, help='Expects path to .txt file that will be tokenized using UDPipe')
train_tokenize.add_argument('--train', '-t', type=str, help='Trains UDPipe on a given treebank, expects treebank language code as input such as "de_gsd"')
train_tokenize.add_argument('--custom_model', '-c', action='store_true', help='If set UDPipe will load custom models instead of the official pre-trained ones.')


sub_name = 'align'
eflomal_args = subparsers.add_parser(sub_name, help='Options for Eflomal alignment tool', parents=[batch_job_options])
eflomal_args.add_argument('input', action='store', help='Input for eflomal')
#delete_parser.add_argument('--file', '-r', default=False, action='store_true',
#                           help='Remove the contents of the directory, too',
#                           )
args = arg_parser.parse_args()
print (args)

from scripts import tokenizer
from scripts import conll

if args.command == 'tokenizer':
    if args.tokenize:
        if args.split:
            tokenizer.split_and_tokenize(args)
        else:
            tokenizer.tokenize(args)

elif args.command == 'conll':
    if args.extract_tokens:
        conll.extract_tokens(args.extract_tokens)
    elif args.parse:
        if args.split:
            assert len(args.parse) == 2, f'When using --split, --parse expects two arguments but got: {len(args.parse)}'
            input_dir, original_filename = args.parse
            assert os.path.isdir(input_dir), 'Argument needs to be a directory when --split is used.'
            conll.parse_split(input_dir, original_filename)
        else:
            assert len(args.parse) == 1, f'--parse expects one argument but got: {len(args.parse)}'
            conll.parse(args.parse[0])





