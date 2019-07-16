# Script replaces characters in all files in the respective target directory

import sys, os
target_dir = os.path.abspath(sys.argv[1])
assert os.path.isdir(target_dir)
replace_pairs = [('\u2028', ' '), ('\x85', '')]

files = os.listdir(target_dir)
files = list(filter(lambda x: not os.path.isdir(os.path.join(target_dir, x)), files))
print(f'Processing directory: {target_dir} ..')
for file in files:
    print(f' - File: {file}')
    file = os.path.join(target_dir, file)
    with open(file) as f:
        data = f.read()
        for pair in replace_pairs:
            data = data.replace(*pair)

    with open(file, 'w') as f:
        f.write(data)
print('Replaced:', replace_pairs)
print('For files in:', target_dir)
