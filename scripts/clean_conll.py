import sys

PATH = sys.argv[1]
PATH_SPLIT = PATH.split('/')
DIR  = '/'.join(PATH_SPLIT[:-1])
NAME = PATH_SPLIT[-1]

with open(PATH) as f:
    lines = []
    for line in f:
        if not line.startswith('#'):
            line = line.split('\t')
            for i in range(2, len(line)):
                line[i] = '_'
            line = '\t'.join(line)

        if not line.endswith('\n'):
            line = line + '\n'
        lines.append(line)
        
if not PATH.endswith('.conll'):
    PATH = PATH+'.conll'
PATH = PATH+'.clean'
with open(PATH, 'w') as f:
    print('Writing to:', PATH)
    f.writelines(lines)
