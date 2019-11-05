

wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh
bash Miniconda2-latest-Linux-x86_64.sh -b -p miniconda

echo "Writing into pn.env"

echo ". $(pwd)/miniconda/etc/profile.d/conda.sh" >> pn.env
echo "conda activate base" >> pn.env
echo 'export PROJECT="$(pwd)"' >> pn.env

. miniconda/etc/profile.d/conda.sh

mkdir bin
BIN_DIR="$(pwd)/bin"

conda activate base
pip install dynet

conda create -n py37 python=3.7 -y
conda activate py37
module purge
module load gcc

pip install numpy
git clone https://github.com/robertostling/eflomal
cd eflomal
make 
install -t $BIN_DIR eflomal
python3 setup.py install
