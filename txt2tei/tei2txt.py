#!/usr/bin/env python3
# v.0.0.1
# Fernando Sanz-Lázaro <fernando.sanz-lazaro@univie.ac.at>
import sys
import re
import os
from bs4 import BeautifulSoup as bs
import pandas as pd


basename = sys.argv[1].split('.')[0]


with open(sys.argv[1], "r", encoding="utf-8") as f:
    soup = bs(re.sub(r'[\s\n]+', ' ', f.read()), 'html.parser')

teiheader = soup.teiheader
filedesc = teiheader.filedesc
titlestmt = filedesc.titlestmt
if titlestmt.find('title', attrs={'type': 'main'}):
    title = titlestmt.find('title', attrs={'type': 'main'}).get_text().strip()
else:
    title = titlestmt.find('title', attrs={'type': None}).get_text().strip()
subtitle = titlestmt.find('title', attrs={'type': 'sub'})
if subtitle:
    subtitle = titlestmt.find(
        'title', attrs={
            'type': 'sub'}).get_text().strip()
else:
    subtitle = ''


persname = titlestmt.persname.get_text().strip()
persname = re.sub('[\n ]{2,}', ' ', persname)
author_ids = titlestmt.find_all('idno')

########
publicationstmt = filedesc.publicationstmt
authority = publicationstmt.authority.get_text().strip()
editdate = publicationstmt.authority.get_text().strip()


sourcedesc = filedesc.sourcedesc

origdate = sourcedesc.find(re.compile('^date$', re.I),
                           attrs={'type': re.compile('^print$', re.I)})
if 'when' in origdate:
    origdate = origdate['when']
else:
    origdate = ''
originalsource = sourcedesc.find(re.compile('^bibl$', re.I),
                                 attrs={'type':
                                        re.compile('^originalSource$', re.I)},
                                 recursive=True).get_text().strip()


particdesc = teiheader.particdesc
listperson = teiheader.listperson
for tag in listperson.find_all(re.compile('^person$', re.I)):
    name = tag.persname.get_text().strip()
    id = tag['xml:id']
    sex = tag['sex']
    #print(f'{name} {id} {sex}')


textclass = teiheader.textclass
keywords = textclass.keywords
genretitle = keywords.find('term',
                           attrs={'type': 'genreTitle'}).get_text().strip()
genreusubitle = keywords.find('term', attrs={'type': 'genreSubtitle'})
genresubitle = ''

text_file = f'<a>{persname}\n<t>{title}\n<g>{genretitle}\n'\
    f'<s>{genresubitle}\n<o>{originalsource}\n<f>{origdate}\n'
text = soup.find('text')
front = text.front
castlist = front.castlist
lista_personajes = ''

if castlist:
    for personaje in castlist.find_all(re.compile('^castItem', re.I)):
        if len(castlist) > 0:
            lista_personajes += '*'
        lista_personajes += personaje.get_text().strip()
    text_file += f'<el>{lista_personajes.strip("*")}\n'

body = soup.body
actos = body.find_all(re.compile('^div$', re.I))
# attrs={'type':re.compile('^act$', re.I)})
if len(actos) < 1:
    actos = [body]
n = 1
tab = '\t'
for acto in actos:
    if len(actos) > 1:
        text_file += f'<j>{n}\n'
        n += 1
    for entrada in acto.findChildren(recursive=False):
        if entrada.name == 'stage':
            text_file += f'<i>{entrada.text.strip()}\n'
        elif entrada.name == 'sp':
            who = entrada.attrs['who'].strip()
            if entrada.speaker:
                speaker = entrada.speaker.text.strip()
            elif entrada.stage:
                speaker =  entrada.stage.text.strip()
            else:
                speaker = who
            text_file += f'{speaker} {who}\n'
            if entrada.lg:
                entrada = entrada.lg
            lines = entrada.findChildren(recursive=False)
            lineout = ''
            for line in lines:
                texto = line.text.strip()
                if line.name == 'stage':
                    lineout = f'<i>{texto}\n'
                elif line.name == 'l':
                    if line.has_attr('part') and line['part'] != 'I':
                        tab += '\t'
                    lineout = f'{tab}{texto}\n'
                else:
                    pass
                text_file += f'{lineout}'
                if line.has_attr('part') and line['part'] == 'F':
                    tab = '\t'

        else:
            pass

with open(f'{basename}_conv.txt', 'w') as f:
    f.write(text_file)
