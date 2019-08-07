# Script takes conll file output by udpipe and extracts the tokenized tokens.
# Newline will only be added if SpacesAfter is '\n'

import sys
file = sys.argv[1]
with open(file) as f:
    print('Opening file:', file)
    lines = []
    line  = []
    for token_line in f:
        if (not token_line.startswith('#')) and (token_line != '\n'): # ignores newlines and those starting with #
            token_line = token_line.split('\t')
            line_no, token = token_line[0], token_line[1] # extract token
            if not ('-' in line_no):
                line.append(token_line[1])                # adding token to current line

            if token_line[9].split('=')[-1] == '\\n\n':   # checks for newline
                lines.append(' '.join(line) + '\n')       # joins tokens with newline at the end
                line = []                                 # initialize new line
outpath = '.'.join(file.split('.')[:-1] + ['txt'])
with open(outpath, 'w') as f:
    print('Writing tokens to:', outpath)
    f.writelines(lines)