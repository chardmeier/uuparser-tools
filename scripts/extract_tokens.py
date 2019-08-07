# Script takes conll files from input directory.
# Newline will only be added if SpacesAfter at index 9 is '\n' (SpacesAfter=\n)

import sys, re, os, pprint
# arg1: target directory, should be the main corpus directory that contains the conll directory
main_dir  = os.path.abspath(sys.argv[1])

# set ending of output files  (dot (.) must be included !):
ending = '' # '.token'

input_dir = os.path.join(main_dir, 'conll')
assert os.path.isdir(input_dir)

output_dir  = os.path.join(main_dir, 'tokens')

if not os.path.isdir(output_dir):
    print('Create directory:', output_dir)
    os.mkdir(output_dir)

print('Loading directory: ', input_dir)

files = list(filter(lambda f: f.endswith('.conll'), os.listdir(input_dir)))
print('Found .conll files:',)
pprint.pprint(files)
print()
print('Output directory:', output_dir)
print()
for file in files:
    in_path = os.path.join(input_dir, file)
    with open(in_path) as f:
        print('Reading file:', in_path)
        lines = []
        line  = []
        for token_line in f:
            if (not token_line.startswith('#')) and (token_line != '\n'):
                token_line = token_line.split('\t')
                line_no, token = token_line[0], token_line[1] # extract token
                if not ('-' in line_no):
                    line.append(token_line[1])  
                n = re.findall(r'\\n', token_line[9])
                if n:
                    lines.append(' '.join(line) + '\n'*len(n))
                    line = []
                    
    out_file = '.'.join(file.split('.')[:-1]) + ending
    out_path = os.path.join(output_dir, out_file)
    with open(out_path, 'w') as f:
        print(' \u2b91  writing tokens to:', out_path)
        f.writelines(lines)
    print()


"""# Script takes conll file output by udpipe and extracts the tokenized tokens.
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
    f.writelines(lines)"""