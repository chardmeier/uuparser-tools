# Pronouns Pipeline Tool for Kebnekaise

Pipeline tool to process pronouns on Kebnekaise cluster using slurm-jobs. 

## Installation 

1. Clone repo
```
git clone https://github.com/maxtrem/pronouns
cd pronouns
```
2. Install environment
```
sh install_env.sh
```


## Get started

Activate env with:

```
source pn.env
```

### Overview

All tools can be accessed through `./tool.py` command from top level directory. Passing flag `--help` will show a basic explanation of the different functions:

```
$ ./tool.py --help

usage: tool.py [-h] {utils,conll,text,token} ...

  

optional arguments:

-h, --help  show this help message and exit

  

commands:

{utils,conll,text,token}

Tool options:

utils Options for Preprocessing

conll Options for .conll files

text  Text options such as UDPipe Tokenizer

token Options for Eflomal alignment tool
```

Each sub command has also it help functions such as for example `./tool.py utils --help` will show help for `utils`.


## Download UDPModels and UD files

```
./tool.py utils --download udpmodels2.4
./tool.py utils --download ud2.4
```

### Train `UUParser`

After downloading the UD-files it is possible to train models for the `UUParser`. For example this command will train a UUParser on `sv_talbanken`:

```
./tool.py conll --train sv_talbanken
```
<hr>
The shell output shows information about the training job:

1. Location of the job logfile
```
Create directory: .. ronouns/logfiles/UUParser
```
2. Location where the models will be saved
```
Create directory: .. pronouns/models/UUParser
```
3. Information about the batch job:
```
tp_sv_talbanken Submitted batch job 9222050
```

4. The batch file location:
```
Batchfile location: /home/t/trembczm/pfs/test/pronouns/batchfiles/history/9222050.sh
```
Note: Models for `UUParser` will be saved at `pronouns/models/UUParser`. The directory contains further directories with the model files:
```
$ ls models
cs_pdt  de_gsd  en_ewt  fr_ftb  fr_gsd  no_bokmaal  sv_talbanken
```
There may be different UD corpora for a language. To decide which model is used please adjust the dictionary in `scripts/config.py`:

```
parser_default_mappings = {'de':'de_gsd', 'en':'en_ewt', 'cs':'cs_pdt', 'fr':'fr_gsd', 'sv':'sv_talbanken', 'no':'no_bokmaal'}
```

The ***key*** of the dictionary corresponds with the language abbreviation used for the  corpus files while the ***value*** corresponds with the model directory name shown before. 

## Corpora
Some corpora have scripts to download them. They will be stored in the `data` directory:

*news-commentary-v14*:
```
./tool.py utils --download news
```

*jw300* can be downloaded as well. With the following command:

```
./tool.py utils --download jw300.l1-l2
```
Where `l1` and `l2` are the language abbreviations. An example would be: `jw300.no-en`

Same syntax applies for *europarl* where an download command would be:

```
./tool.py utils --download europarl.de-en
```



## Pipeline

We go through the pipeline with the news-commentary corpus as an example:

### 1. Download the corpus:

```
./tool.py utils --download news
```

### 2. Substitute links and other problematic characters

Substitute links, mail addresses or other character combinations that could be problematic for the tokenizer. Replaced parts will be displayed throughout the process and saved in the corpus directory in `link.dict`.

```
./tool.py utils --sublinks data/news-commentary-v14/
```

*The substitution can be undone with the `--resublinks` command.*

### 3. Tokenize
Next step is tokenizing. We continue now using the language pair `de-en`. To start the tokenizing jobs use the following commands:

```
./tool.py text --tokenize data/news-commentary-v14/news-commentary-v14.de-en.de --split --nl2x
./tool.py text --tokenize data/news-commentary-v14/news-commentary-v14.de-en.en --split --nl2x
```
#### Explanation of the command parts:

- `text` is the submodule that is used raw text. This was necessary as some commands like `--train` are can be used differently.
- `--tokenize` indicates tokenizing using `UDPipe` 
- next follows the data location
- `--split` *(optional)* will split the original file into smaller files where each file gets its own `slurm` job. This makes it possible to later-on parse larger files and will speed up the whole process. To disable the splitting just leave out the flag.
- `--split_size` *(optional)* To modify the size for each split part use this argument. Default is *100000* lines.
- `--nl2x` This command will double all `\n` (newline) characters. This is necessary to force `UDPipe` to end sentences before a newline. Otherwise it will mess up the sentence alignment as `UDPipe` sometimes continues the sentence after a `\n`. 

***Notes:***
The shell output gives information about input, where the output will be saved as well location of the created batch file that is being used for later review:

```
Reading file: .. pronouns/data/news-commentary-v14/PART_01___news-commentary-v14.de-en.en
Tokenized file will be saved to: .. pronouns/data/news-commentary-v14/conll
Using UDPipe model: .. pronouns/models/UDPipe/english-ewt-ud-2.4-190531.udpipe
tk_en_ewt Submitted batch job 9222111
Batchfile location: .. pronouns/batchfiles/history/9222111.sh
```

This step also applies some minor preprocessing like replacement of problematic space characters.

The model will be chosen automatically. Where the last part of the language keys are used *de-en.__en__*  resp. *de-en.__de__*.
Later steps will also make use of the other language keys *__de-en__.en* therefore please always maintain the this format in the filenames: ___L1-L2.L1___ resp. ___L1-L2.L2___!

### 4. Parse

When the tokenized `.conll` files are ready we can start parsing. To parse the output of `UDPipe` we use the following commands:
```
./tool.py conll --parse data/news-commentary-v14/conll/ -s de-en.de
./tool.py conll --parse data/news-commentary-v14/conll/ -s de-en.en
```
#### Explanation of the command parts:
- `conll` submodule for `.conll` files
- `--parse` indicates parsing using the `UUParser`. Takes as argument a `.conll` file or a directory when using `--split` option. 
- `-s` or `--split` *(optional)* takes as argument the language keys (`de-en.en`) to identify the correct parts. If `--split` is not set `--parse` expects a single `.conll` file as input.

***Notes:***

This will again display some information in the shell such as the parts that were found:

```
Input: de-en.de
Full match-string: PART_\d+___.*de-en.de.*\.conll
Found parts in "data/news-commentary-v14/conll/":
['PART_00___news-commentary-v14.de-en.de.conll',
'PART_01___news-commentary-v14.de-en.de.conll',
'PART_02___news-commentary-v14.de-en.de.conll',
'PART_03___news-commentary-v14.de-en.de.conll']
```

As well as input and output of the job and the batch file and job id:

```
Reading file: /pfs/nobackup/home/t/trembczm/test/pronouns/data/news-commentary-v14/conll/PART_00___news-commentary-v14.de-en.de.conll
Input directory:  /pfs/nobackup/home/t/trembczm/test/pronouns/data/news-commentary-v14/conll
Output directory: /pfs/nobackup/home/t/trembczm/test/pronouns/data/news-commentary-v14/parsed

parse_de Submitted batch job 9222150
Batchfile location: /home/t/trembczm/pfs/test/pronouns/batchfiles/history/9222150.sh
```

### 5. Merge

.. comming soon ..
