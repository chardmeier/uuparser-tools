import collections
import re
import sys

s = ''.join(chr(c) for c in range(sys.maxunicode+1))
ws = set(re.findall(r'\s', s)) - {'\n', ' ', '\t'}

with open(sys.argv[1], 'r') as f:
    out = collections.defaultdict(list)
    for i, line in enumerate(f):
        found = set(line).intersection(ws)
        if found:
            out[frozenset(found)].append((i, line))
verbose = False
if len(sys.argv) > 2:
    p2 = sys.argv[2]
    verbose = p2 == '-v'
for s, e in out.items():
    print('***', s, '-', len(e))
    if verbose:
        for t in e:
            print(t)
        print()
