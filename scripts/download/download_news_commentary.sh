#!/bin/bash
# creates new file names for both languages
create_filenames ()	{
    NAME="$(cut -d'.' -f1 <<<$FILENAME)"
    L1="$(cut -d'-' -f1 <<<$LP)"
    L2="$(cut -d'-' -f2 <<<$LP)"
    FILENAME_L1=$NAME.$LP.$L1
    FILENAME_L2=$NAME.$LP.$L2
}

# substitutes language pair into link
substitute_link (){
    LINK="http://data.statmt.org/news-commentary/v14/training/news-commentary-v14.${LP}.tsv.gz"
    FILENAME_GZ="news-commentary-v14.${LP}.tsv.gz"
    FILENAME="news-commentary-v14.${LP}.tsv"
}
pairs="de-en en-fr cs-en"
# possible: en-fr de-en cs-en # cs-de cs-fr de-fr de-nl

mkdir news-commentary-v14
cd news-commentary-v14

for LP in $pairs
do 
    substitute_link
    create_filenames
    wget $LINK
    gunzip $FILENAME_GZ
    cut -f1 $FILENAME > $FILENAME_L1
    cut -f2 $FILENAME > $FILENAME_L2
    rm $FILENAME
done

