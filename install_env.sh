#! /bin/bash

set -e

. "/pfs/nobackup/home/c/chriha/miniconda3/etc/profile.d/conda.sh"

MAIN="$(pwd)"

mkdir -p software
SOFTWARE="$(pwd)/software"

mkdir -p $SOFTWARE/bin
BIN_DIR="$SOFTWARE/bin"

echo "Writing into pn.env"

echo ". $HOME/pfs/miniconda3/bin/activate uuparser" >> pn.env
echo "export PROJECT=$(pwd)" >> pn.env
echo "" >> pn.env
echo "module load GCC " >> pn.env
echo "export SOFTWARE=$SOFTWARE" >> pn.env
echo "export BIN_DIR=$BIN_DIR" >> pn.env
echo "export PATH=$BIN_DIR:\$PATH" >> pn.env
#echo "module load python3/3.7.0.gnu"

# . $HOME/pfs/miniconda3/etc/profile.d/conda.sh
conda create -n uuparser python=3 numpy==1.16.1 cython

cd $SOFTWARE

wget -q https://github.com/ufal/udpipe/releases/download/v1.2.0/udpipe-1.2.0-bin.zip
unzip -q udpipe-1.2.0-bin.zip
rm udpipe-1.2.0-bin.zip
mv $SOFTWARE/udpipe-1.2.0-bin/bin-linux64/udpipe $BIN_DIR/


conda activate uuparser
conda install cython
#pip install dynet

git clone https://github.com/maxtrem/uuparser
pip install -r uuparser/requirements.txt
pip install --ignore-installed opustools-pkg
#conda create -n py37 python=3.7 -y
#conda activate py37
#module purge
#module load GCC

pip install numpy
git clone https://github.com/robertostling/eflomal
cd eflomal
make 
install -t $BIN_DIR eflomal
python setup.py install



echo "Environment installation script finished. Use 'source pn.env' to activate."

