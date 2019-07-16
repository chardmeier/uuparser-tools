# Script moves '\u2028' from line to spaces af SpacesAfter position

import sys
file = sys.argv[1]
n_char = '\u2028'


print(sys.argv[2] == n_char)

with open(file) as f:
    print('Opening file:', file)
    lines = []
    line  = []
    for i, line in enumerate(f):
        if n_char in line:
            print(f'Line {i}:')
            print(line)
            line = line.replace(n_char, '')
            if not line.startswith('#'):
                line = line.split('\t')
                line[9] = 'SpacesAfter={}'.format(repr(n_char).strip("'"))
                line = '\t'.join(line)
            line += '\n'
            print('Changed to:')
            print(line)
        lines.append(line)
        
outpath = '.'.join(file.split('.')[:-1] + ['test'])
with open(outpath, 'w') as f:
    print('Writing tokens to:', outpath)
    f.writelines(lines)
