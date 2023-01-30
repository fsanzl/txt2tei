[![License: GPL](https://img.shields.io/github/license/fsanzl/txt2tei)](https://opensource.org/licenses/GPL-3.0)
<!--- [![Version: 1.0.1-2](https://img.shields.io/github/v/release/fsanzl/txt2tei?include_prereleases)](https://pypi.org/project/txt2tei/)
# [![Python versions: 3.5, 3.6, 3.7, 3.8, 3.9](https://img.shields.io/pypi/pyversions/txt2tei)](https://pypi.org/project/txt2tei/) -->

<h2 align="center">TXT2TEI</h2>
<h3 align="center">An aid to encoding plays as XML-TEI</h2>


*txt2tei*  is a Python script to encode Spanish Siglo de Oro plays as XML-TEI files. It takes a minimally annotated tabular TXT file resembling the printed layout with a reduced set of simple tags. The script speeds up the process of encoding TEI files by automating their annotation, requiring just an (almost) visual edition of the sourceTXT files.

These scripts are part of the research project [Sound and Meaning in Spanish Golden Age Literature](https://soundandmeaning.univie.ac.at/).

## Requirements

The programme requires following libraries:

* BeautifulSoup 4
* pandas
* datetime
* unidecode
* lxml

txt2tei runs on lxml and tei2txt on BS4. They may be unified in the future though. 


# Installation

Download the python scripts and the files sexos.csv, config.py and authors.xml in the same directory


## Use

Edit config.py with your edition data and run the following commands:

```bash
./txt2tei.py tabularfile.txt
```

Additionally, the script tei2txt.py performs the inverse operation
```bash
./tei2txt.py xmlteifile.xml
```

## Description

The tabular file must follow the following conventions:
```
<x>Comment
<a>Author's name (Just one single word, e.g. Calderón, Lope, Tirso...
<t>Title
<g>Genre
<s>Subgenre
<o>Source*URL
<f>Date
<x> The tag el marks the dramatis personae of  <castList>
<el>DRAMATIS PERSONAE (optional)|CHARACTER 1, a character*CHARACTER 2, another character*CHARACTER 3, a third one*CHARACTER 4, and just one more
<j>Act
<sc>Scene
<i>Stage direction
<x>Comment
CHARACTER ONE
<x>A tabulator marks the speeches
        Verse 1,
        verse 2.
CHARACTER 2
        <i>Internal stage direction
        Verse 3
        verse 4 (beginning)
CHARACTER 1
                Verse 4 (middle)
<x>An additional tab marks the continuation of a shared verse
CHARACTER 3
                        Verse 4 (end)
    verse 5,
    verse 6.
  ...
MUSIC
<e>Echo
CHARACTER 4
        <i>Reads:
<p>Prose
MULTIPLE CHARACTERS #character1 #character2
<x> Instead of letting the programme guess the characters in a collective parlamente, they can be indicated here explicitly
```

In order toi assign sexes to the characters, there is a CSV file in the format:

```csv
NAME,MALE,True
```

The first field is the name, the second the sex, and the third if was manully checked. This can be done with the provided script makelist.py

## Known issues

The programme only recognises "Calderón", "Lope" and "Calderón (atri.)" as authors. Adding new authors is trivial, as they can just be added to the dictionary authors.

Lope's ids are placeholders. Proper numbers should be given.

Most important: The programme is aimed to Spanish 17th century plays. The language conventions (e.g., this is an issue concerning sex of collective characters or a shared parlament in which 'Y' will be parsed as 'AND') and structure (versified plays) may need some tinkering to be applied to other kind of plays.


## Contributions

Feel free to contribute using the [GitHub Issue Tracker](https://github.com/fsanzl/txt2tei/issues) for feedback, suggestions, or bug reports.


## Licence

This project is under GNU GPL 3. See [LICENCE](https://github.com/fsanzl/txt2tei/LICENSE) for details.

