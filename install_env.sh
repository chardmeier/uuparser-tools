

#wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh
#bash Miniconda2-latest-Linux-x86_64.sh -b -p miniconda

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p miniconda

rm Miniconda3-latest-Linux-x86_64.sh

MAIN="$(pwd)"

mkdir software
SOFTWARE="$(pwd)/software"

mkdir $SOFTWARE/bin
BIN_DIR="$(pwd)/bin"

echo "Writing into pn.env"

echo ". $(pwd)/miniconda/etc/profile.d/conda.sh" >> pn.env
echo "conda activate base" >> pn.env
echo "PROJECT=""$(pwd)" >> pn.env
echo "" >> pn.env
echo "module load GCC " >> pn.env
echo "SOFTWARE=$SOFTWARE" >> pn.env
echo "BIN_DIR=$BIN_DIR" >> pn.env
echo "PATH=$BIN_DIR:\$PATH" >> pn.env
#echo "module load python3/3.7.0.gnu"

. miniconda/etc/profile.d/conda.sh

cd $SOFTWARE

wget https://github.com/ufal/udpipe/releases/download/v1.2.0/udpipe-1.2.0-bin.zip
unzip udpipe-1.2.0-bin.zip
rm udpipe-1.2.0-bin.zip
mv $SOFTWARE/udpipe-1.2.0-bin/bin-linux64/udpipe $BIN_DIR/


conda activate base
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



echo "Envoroment installation script finished. Use 'source pn.env' to activate."