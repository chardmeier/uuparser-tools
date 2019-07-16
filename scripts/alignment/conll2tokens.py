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
