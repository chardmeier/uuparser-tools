#!/bin/sh

echo "Downloading treebanks v2.4"
curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2988{/ud-treebanks-v2.4.tgz}
tar -zxf ud-treebanks-v2.4.tgz
rm treebanks.tgz
