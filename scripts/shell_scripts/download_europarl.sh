#!/bin/sh 
DIR=$3
L1=$1
L2=$2

cd $DIR
wget http://www.statmt.org/europarl/v7/"$L1-$L2.tgz"

tar -xzvf $L1-$L2.tgz
rm $L1-$L2.tgz
