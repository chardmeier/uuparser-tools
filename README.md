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
Reading file: .. pronouns/data/news-commentary-v14/conll/PART_00___news-commentary-v14.de-en.de.conll
Input directory:  .. pronouns/data/news-commentary-v14/conll
Output directory: .. pronouns/data/news-commentary-v14/parsed

parse_de Submitted batch job 9222150
Batchfile location: .. pronouns/batchfiles/history/9222150.sh
```


### 5. Merge

Now that we have finished the parsing we can merge the split parts again by using the following command.

```
./tool.py conll --merge pronouns/data/news-commentary-v14/parsed de-en.de —nl2x
./tool.py conll --merge pronouns/data/news-commentary-v14/parsed de-en.en —nl2x
```

#### Explanation of the command parts:

- `--merge` takes as first argument the directory to the `.conll` files that should be merged and as second argument a the language key (`de-en.de`) for to identify the respective parts.
- `-nl2x` adding this flag will remove the doubled newline (`\n`) characters again

***Notes:***
As before the shell output will display which files will be merged and where they will be saved:

```
Input: de-en.de
Full match-string: PART_\d+___.*de-en.de.*\.conll
Found parts in "pronouns/data/news-commentary-v14/parsed":
['PART_00___news-commentary-v14.de-en.de.conll',
'PART_01___news-commentary-v14.de-en.de.conll',
'PART_02___news-commentary-v14.de-en.de.conll',
'PART_03___news-commentary-v14.de-en.de.conll']

Merged output will be saved to:
pronouns/data/news-commentary-v14/parsed/news-commentary-v14.de-en.de.conll
.. processing (starting at sent 1): PART_00___news-commentary-v14.de-en.de.conll
.. processing (starting at sent 105260): PART_01___news-commentary-v14.de-en.de.conll
.. processing (starting at sent 210471): PART_02___news-commentary-v14.de-en.de.conll
.. processing (starting at sent 316047): PART_03___news-commentary-v14.de-en.de.conll
```

### 6. Re-Substitute links and other problematic symbols

Now we can replace the placeholders that where inserted in step 2. by the tokens / sequences again:

```
./tool.py conll --resublinks data/news-commentary-v14/parsed/news-commentary-v14.de-en.de.conll
./tool.py conll --resublinks data/news-commentary-v14/parsed/news-commentary-v14.de-en.en.conll
```

The shell output will display the replacements.

### 7. Extract tokens from `.conll`

Now we can extract the tokens from the created `.conll` files and get them into sentence aligned format again:

```
./tool.py conll -e data/news-commentary-v14/parsed/
```

The shell output states which files are taken as input as well where the output is saved to. The number of lines for the output lines is displayed as well.

```
Input directory:  pronouns/data/news-commentary-v14/parsed
Output directory: pronouns/data/news-commentary-v14/tokens

  

Directory: pronouns/data/news-commentary-v14/parsed

Found ['.conll'] files:
['news-commentary-v14.de-en.de.conll', 'news-commentary-v14.de-en.en.conll']

Reading file: pronouns/data/news-commentary-v14/parsed/news-commentary-v14.de-en.de.conll
⮑  writing tokens (676570 lines) to: pronouns/data/news-commentary-v14/tokens/news-commentary-v14.de-en.de.token

Reading file: pronouns/data/news-commentary-v14/parsed/news-commentary-v14.de-en.en.conll
⮑  writing tokens (676570 lines) to: pronouns/data/news-commentary-v14/tokens/news-commentary-v14.de-en.en.token
```


### 8.  Create `.chr` format *(optional)*
 
 To create token output in `.chr` format use the following command:

```
./tool.py conll -c data/news-commentary-v14/parsed/
```

This extracts the tokens from `.conll` and stores the output in `.chr` the corpus  directory in the directory `chr_format`.

The shell output displays input and output files:

```
Input directory:  pronouns/data/news-commentary-v14/parsed
Output directory: pronouns/data/news-commentary-v14/chr_format

Directory: pronouns/data/news-commentary-v14/parsed

Found ['.conll'] files:
['news-commentary-v14.de-en.de.conll', 'news-commentary-v14.de-en.en.conll']

Reading file: pronouns/data/news-commentary-v14/parsed/news-commentary-v14.de-en.de.conll
676570 line ids written.
⮑  writing chr-format output (703189 overall lines) to: pronouns/data/news-commentary-v14/chr_format/news-commentary-v14.de-en.de.chr

Reading file: pronouns/data/news-commentary-v14/parsed/news-commentary-v14.de-en.en.conll
676570 line ids written.
⮑  writing chr-format output (695048 overall lines) to: pronouns/data/news-commentary-v14/chr_format/news-commentary-v14.de-en.en.chr
```


### 9. Word alignment

The word alignment batch job is started using the following command.
```
./tool.py token --align data/news-commentary-v14/tokens/
```
The command does not only the word alignment it also creates fast text files from `.token` files from the `token` directory:
```
Pairs found:
{'de-en': {'de': 'news-commentary-v14.de-en.de.token',
           'en': 'news-commentary-v14.de-en.en.token'}}
```

Output in fast text format is saved to the directory `merged`:
```
['news-commentary-v14.de-en.fast_text', 'news-commentary-v14.en-de.fast_text']
```

This format does not accept empty lines. Therefore all empty lines are removed before merging. The line numbers are stored for each file in a dictionary file `empty.dict` in the `merged` directory.

After that the word alignment job is submitted for the fast text files using `eflomal`. For the fast text file creation again it is important to keep the naming routine in the format ___L1-L2.L1___ at the end of the file. This is needed to correctly associate the correct language pairs for the merging part.
The alignment output is stored in a directory `alignment` in the corpus directory.

All important information is stated in the shell output:

```
Input directory: pronouns/data/news-commentary-v14/tokens
Output directory: pronouns/data/news-commentary-v14/merged

de-en
Pairs found:
{'de-en': {'de': 'news-commentary-v14.de-en.de.token',
           'en': 'news-commentary-v14.de-en.en.token'}}
Merging..
Writing: pronouns/data/news-commentary-v14/merged/news-commentary-v14.de-en.fast_text
Writing: pronouns/data/news-commentary-v14/merged/news-commentary-v14.en-de.fast_text
.. done.

Input directory:  pronouns/data/news-commentary-v14/merged
Output directory: pronouns/data/news-commentary-v14/alignment

Valid input files  ("pronouns/data/news-commentary-v14/merged"):
['news-commentary-v14.de-en.fast_text', 'news-commentary-v14.en-de.fast_text']
Create and submit batchfiles..
Create directory: pronouns/logfiles/alignment

al_de-en Submitted batch job 9224669
Batchfile location: pronouns/batchfiles/history/9224669.sh
al_en-de Submitted batch job 9224670
Batchfile location: pronouns/batchfiles/history/9224670.sh
```
### 10. Add empty lines again

Finally we need to add the empty lines again that were removed in step 9.:

```
./tool.py utils --ft_add_n data/news-commentary-v14/alignment/
```
Shell output:
```
Directory: pronouns/data/news-commentary-v14/alignment

Found ['.rev', '.fwd'] files:
['news-commentary-v14.de-en.fwd',
'news-commentary-v14.de-en.rev',
'news-commentary-v14.en-de.fwd',
'news-commentary-v14.en-de.rev']

Processing: pronouns/data/news-commentary-v14/alignment/news-commentary-v14.de-en.fwd ..
Empty lines successfully added.
Processing: pronouns/data/news-commentary-v14/alignment/news-commentary-v14.de-en.rev ..
Empty lines successfully added.
Processing: pronouns/data/news-commentary-v14/alignment/news-commentary-v14.en-de.fwd ..
Empty lines successfully added.
Processing: pronouns/data/news-commentary-v14/alignment/news-commentary-v14.en-de.rev ..
Empty lines successfully added.
```

Now we are done! The final directory tree structure will look like this:

```
$ tree data/news-commentary-v14/
data/news-commentary-v14/
├── alignment
│   ├── news-commentary-v14.de-en.fwd
│   ├── news-commentary-v14.de-en.priors
│   ├── news-commentary-v14.de-en.rev
│   ├── news-commentary-v14.en-de.fwd
│   ├── news-commentary-v14.en-de.priors
│   └── news-commentary-v14.en-de.rev
├── chr_format
│   ├── news-commentary-v14.de-en.de.chr
│   └── news-commentary-v14.de-en.en.chr
├── conll
│   ├── PART_00___news-commentary-v14.de-en.de.conll
│   ├── PART_00___news-commentary-v14.de-en.en.conll
│   ├── PART_01___news-commentary-v14.de-en.de.conll
│   ├── PART_01___news-commentary-v14.de-en.en.conll
│   ├── PART_02___news-commentary-v14.de-en.de.conll
│   ├── PART_02___news-commentary-v14.de-en.en.conll
│   ├── PART_03___news-commentary-v14.de-en.de.conll
│   └── PART_03___news-commentary-v14.de-en.en.conll
├── link.dict
├── merged
│   ├── empty.dict
│   ├── news-commentary-v14.de-en.fast_text
│   └── news-commentary-v14.en-de.fast_text
├── news-commentary-v14.cs-en.cs
├── news-commentary-v14.cs-en.en
├── news-commentary-v14.de-en.de
├── news-commentary-v14.de-en.de.parts
├── news-commentary-v14.de-en.en
├── news-commentary-v14.de-en.en.parts
├── news-commentary-v14.en-fr.en
├── news-commentary-v14.en-fr.fr
├── parsed
│   ├── news-commentary-v14.de-en.de.conll
│   ├── news-commentary-v14.de-en.en.conll
│   ├── PART_00___news-commentary-v14.de-en.de.conll
│   ├── PART_00___news-commentary-v14.de-en.en.conll
│   ├── PART_01___news-commentary-v14.de-en.de.conll
│   ├── PART_01___news-commentary-v14.de-en.en.conll
│   ├── PART_02___news-commentary-v14.de-en.de.conll
│   ├── PART_02___news-commentary-v14.de-en.en.conll
│   ├── PART_03___news-commentary-v14.de-en.de.conll
│   └── PART_03___news-commentary-v14.de-en.en.conll
├── PART_00___news-commentary-v14.de-en.de
├── PART_00___news-commentary-v14.de-en.en
├── PART_01___news-commentary-v14.de-en.de
├── PART_01___news-commentary-v14.de-en.en
├── PART_02___news-commentary-v14.de-en.de
├── PART_02___news-commentary-v14.de-en.en
├── PART_03___news-commentary-v14.de-en.de
├── PART_03___news-commentary-v14.de-en.en
└── tokens
    ├── news-commentary-v14.de-en.de.token
    └── news-commentary-v14.de-en.en.token

6 directories, 48 files
```

