#!/bin/sh 
PATH=$3
L1=$1
L2=$2

echo "Downloading JW300 for languages: $L1 and $L2"
miniconda/bin/opus_read -d JW300 \
                        --source $L1 \
                        --target $L2 \
                        --write_mode moses \
                        --write "$PATH/jw300.$L1" "$PATH/jw300.$L2"

rm JW300_latest_xml_*
