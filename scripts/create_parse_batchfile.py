import sys
_, code, path = sys.argv

s = f"""#!/bin/bash

#SBATCH -t 48:00:00
#SBATCH -n 1
#SBATCH -J "parse_{code}"
#SBATCH --mem-per-cpu=48GB
#SBATCH --account=nn9447k
#SBATCH --output=/usit/abel/u1/trembczm/pronoun_project/logfiles/parse_{code}-%j.out

source ~/.bashrc

PARSER="/usit/abel/u1/trembczm/pronoun_project/uuparser/barchybrid"
MODELDIR="/usit/abel/u1/trembczm/pronoun_project/parser_out"
OUTDIR="/usit/abel/u1/trembczm/pronoun_project/parsed/"
DATADIR="/usit/abel/u1/trembczm/pronoun_project/ud-treebanks-v2.4"

cd $PARSER
python src/parser.py --predict \
        --outdir $OUTDIR/ \
        --modeldir $MODELDIR/{code}/ \
        --disable-pred-eval \
        --graph-based \
        --testfile {path}"""

out_path = '/usit/abel/u1/trembczm/pronoun_project/batchfiles/parse_batchfile.sh'
with open(out_path, 'w') as f:
    f.write(s)
print('Batchfile written to:', out_path)
