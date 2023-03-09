#!/usr/bin/env python
import pandas as pd
from sys import argv
from lxml.etree import parse, tostring
import re


def get_namespace(element):
    m = re.match('\{.*\}', element.tag)
    return m.group(0) if m else ''


df = pd.read_csv('corpus.csv')
tree = parse(rf'{argv[1]}')
root = tree.getroot()
namespace = get_namespace(root)

title = root.find(rf'.//{namespace}title[@type="main"]').text
if not title:
    title = root.find(rf'.//{namespace}title').text

lineas = root.findall(f'.//{namespace}l')
for tag in lineas:
    if 'n' in tag.attrib:
        n = tag.attrib['n']
        print(n)
        metre = df.loc[(df['Title'] == title) & (df['Verse'] == int(n)),
                       'Rhythm'].values[0]
        tag.attrib['met'] = metre

with open("output.xml", "w") as f:
    f.write(tostring(root, pretty_print=True, encoding='unicode'))
# root.write('output.xml', pretty_print=True)
