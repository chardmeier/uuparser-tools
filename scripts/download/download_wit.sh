#!/bin/sh

echo "Downloading files from: https://wit3.fbk.eu/mt.php?release=2016-01"
SAVE_DIR="WIT"

mkdir $SAVE_DIR
cd $SAVE_DIR

wget -i ~/pronoun_project/scripts/download/links/wit.txt 

for filename in *.tgz
do
  tar -zxf $filename
done

rm *.tgz
