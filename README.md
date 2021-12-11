
#Korean Reader

## Web server

A tool to help to read korean texts with a popup dictionary. It works as a web server.
Run: python webserver.py


## Extraction work tool

A tool to split Korean text into individual words to look up definitions easily and save them for further learning.

Usage *word_extraction.py <input file> <output file> [--tag deck_tag]*
Extracts words from the input file and list them in format:
word <TAB> definition <TAB> hanja <TAB> sentence <TAB> tag

## File strucuture

- kreader: this directory.
- kreader_dicts: clone https://github.com/xiaolanchong/kreader_dicts repo.
- kreader_db: directory to store the sqlite database file, create an empty directory if does not exist.

## Upgrade

The tool is intended to function without Internet connection at all.
All dependecies are available locally and must be deployed manually.

### JQuery

Download the minimal version at https://jquery.com/download/ and unpack to static/scripts.

### JQuery UI

Download the full archive (the lastest version) at https://jqueryui.com/download/ and unpack to static/scripts.

### Popper

Download the minimal version at https://popper.js.org/ and unpack to static/scripts.

### Tether

Download the minimal version at https://cdnjs.com/libraries/tether and unpack to static/scripts.


### Mecab

Release: https://bitbucket.org/eunjeon/mecab-ko/downloads/
C++ files can be compiled under Linux and Windows (the latter virtually with no autotools required).
Only libmecab.dll or .so required.

Dictionary: https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/
Imho best compiled on Linux, requires autotools. Put files into mecab/mecabrc directory.

## Used technologies

- Python 3.6+
- Flask: Web framework
- SQLAlchemy + sqlite: to store the user's texts
- KoNLPy: Korean natural language processing framework, https://konlpy.org
- JQuery: client side script
- JQuery UI: client side UI
- Bootstrap: client side CSS helper




