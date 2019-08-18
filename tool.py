#!/usr/bin/env python3

import argparse, os

batch_job_options  = argparse.ArgumentParser(add_help=False)
batch_group = batch_job_options.add_argument_group('Batch Job Script options')
batch_group.add_argument('--mem', default='60GB', type=str, help='Sets amount of memory allocated for the job. For example "60GB"')
batch_group.add_argument('--duration', '-d', default='96:00:00', type=str, help='Sets the TimeLimit for the job. For example "96:00:00"')
batch_group.add_argument('--name', '-n', type=str, help='Option for setting a manual name for batch job.')
batch_group.add_argument('--partition', type=str, choices=['normal', 'hugemem', 'accel'], default='normal', help='Setting partition for the job to run on (default=normal).')

other_options  = argparse.ArgumentParser(add_help=False)
other_options_group = batch_job_options.add_argument_group('Other options')
#other_options_group.add_argument('--split', '-s', nargs='?', const=True, default=False, help='If set True, text file will be splitted before tokenizing.')
other_options_group.add_argument('--split_size', type=int, default=150000, help='Sets split size (in lines).')
other_options_group.add_argument('--double_n', action='store_true', help='If set, newlines will be doubled while processing.')





arg_parser = argparse.ArgumentParser()

subparsers = arg_parser.add_subparsers(title="commands", dest="command", help='Tool options:')

sub_name = 'utils'
utils_args = subparsers.add_parser(sub_name, help='Options for Preprocessing ', parents=[batch_job_options])
# use store true, set split size separately 
utils_group = utils_args.add_mutually_exclusive_group(required=True)
utils_group.add_argument('--split', '-s', type=str, help='Selected file will be splited.')



sub_name = 'parser'
uuparser_args = subparsers.add_parser(sub_name, help='Options for UUParser', parents=[batch_job_options])
# use store true, set split size separately 
train_parse = uuparser_args.add_mutually_exclusive_group(required=True)
train_parse.add_argument('--parse', '-p', type=str, help='Expects path to .conll file that will be parsed using UUParser')
train_parse.add_argument('--train', '-t', type=str, help='Trains UUParser on a given treebank, expects treebank language code as input such as "de_gsd"')

sub_name = 'conll'
conll_args = subparsers.add_parser(sub_name, help='Options for .conll files', parents=[batch_job_options])
conll_args.add_argument('--split', '-s', help='Argument must be a match-string that all respective parts share e.g. the original file name like: "europarl-v7.de-en.de"')

conll_parse = conll_args.add_mutually_exclusive_group(required=True)
conll_parse.add_argument('--parse', '-p', type=str,
    help='Argument musst be a .conll file or a directoy containing split .conll-files when --split is set.')
conll_parse.add_argument('--extract_tokens', '-e', type=str, help='Expects path to directory with conll-files from that tokens will be extracted.')
conll_parse.add_argument('--chr', '-c', type=str, help='Expects path to directory with conll-files that will be converted.')
conll_parse.add_argument('--train', '-t', type=str, help='Trains UUParser on a given treebank, expects treebank language code as input such as "de_gsd"')
conll_parse.add_argument('--merge', '-m', metavar=['Directory', 'MatchString', 'OutputName'], type=str, nargs='+', 
    help='Merges all files in the given Directory that match the MatchString e.g. the original file name like: "europarl-v7.de-en.de". OutputName can be set  optionally.')





sub_name = 'text'
text_args = subparsers.add_parser(sub_name, help='Text options such as UDPipe Tokenizer', parents=[batch_job_options])
text_args.add_argument('--split', '-s', action='store_true', help='If set, input file will be splitted before tokenizing.')

train_tokenize = text_args.add_mutually_exclusive_group(required=False)
train_tokenize.add_argument('--tokenize', type=str, help='Expects path to .txt file that will be tokenized using UDPipe')
train_tokenize.add_argument('--train', '-t', type=str, help='Trains UDPipe on a given treebank, expects treebank language code as input such as "de_gsd"')
train_tokenize.add_argument('--custom_model', '-c', action='store_true', help='If set UDPipe will load custom models instead of the official pre-trained ones.')
#train_tokenize.add_argument('--custom_model', '-c', action='store_true', help='If set UDPipe will load custom models instead of the official pre-trained ones.')

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
from scripts import preprocessing
from scripts import utils
from scripts import helpers


if args.command == 'text':
    if args.tokenize:
        if args.split:
            tokenizer.split_and_tokenize(args.tokenize, args.split_size, double_n=args.double_n)
        else:
            tokenizer.tokenize(args.tokenize)

if args.command == 'utils':
    if args.split:
        preprocessing.split(args.split, args.split_size, double_n=args.double_n)


elif args.command == 'conll':
    if args.extract_tokens:
        conll.extract_tokens(args.extract_tokens)
    elif args.merge:
        conll.merge_conll(*args.merge)
    elif args.chr:
        conll.chr_format_dir(args.chr)
    elif args.parse:
        if args.split:
            input_dir = args.parse
            match_string = args.split
            helpers.handle_split(input_dir, match_string, do=conll.parse)
        else:
            conll.parse(args.parse)





