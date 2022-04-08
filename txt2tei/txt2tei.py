#!/usr/bin/env python3
from sys import argv
import re
from datetime import datetime
from unidecode import unidecode
from bs4 import BeautifulSoup
import pandas as pd
import lxml.etree as etree
from lxml.etree import Element, SubElement, ElementTree, parse
from pathlib import Path

hodie = datetime.today().strftime('%Y-%m-%d')
nunc = datetime.today().strftime('%H:%M:%S')
editor = ''
authority = ''
publisher_id = ''
publisher = ''
licence = ''
licence_url = ''

from config import *

input_file = argv[1]
output = f'{argv[1].rsplit(".", 1)[0]}.xml'
if len(argv) > 2:
    edition = argv[2]
else:
    edition = '0.1'
header_labels = {'<t>': 'title', '<tt>': 'subtitle', '<a>': 'author',
                 '<g>': 'genre', '<s>': 'subgenre', '<o>': 'source',
                 '<f>': 'date', '<el>': 'elenco', '<x>': 'comment'}
body_labels = {'j': 'act', '<e>': 'echo', '<p>': 'prose',
               '<i>': 'stage_direction', '<x>': 'comment'}

def make_tree(title, subtitle, author, source, date='1600s'):
    persons_dict = {}
    xml_model = '<?xml-model http://www.tei-c.org/release/xml/tei/custom/'\
        'schema/relaxng/tei_all.rng application/xml http://relaxng.org/ns/'\
        'structure/1.0 http://www.tei-c.org/release/xml/tei/custom/schema/'\
        'relaxng/tei_all.rng application/xml'\
        'http://purl.oclc.org/dsdl/schematron ?>'
    root = Element('TEI')
    tree = etree.ElementTree(root)
    tei_header = SubElement(root, 'teiHeader')
    # fileDesc
    file_desc = SubElement(tei_header, 'fileDesc')
    title_stmt = Element('titleStmt')
    title_stmt = make_title(title_stmt, title, subtitle)
    title_stmt = make_authors(title_stmt, author)
    title_stmt = make_editor(title_stmt, editor)
    file_desc.insert(1, title_stmt)
    # publicationStmt
    publication_stmt = SubElement(file_desc, 'publicationStmt')
    publication_stmt = make_edition(publication_stmt)
    file_desc.insert(1, publication_stmt)
    # srcDesc
    source_desc = SubElement(file_desc, 'sourceDesc')
    make_source(source_desc, source)
    file_desc.insert(1, source_stmt)


    # profileDesc
    profileDesc = SubElement(tei_header, 'profileDesc')
    make_participants()
    SubElement(
        SubElement(
            profileDesc,
            'keywords'),
        'term').set(
            'type',
        'genreTitle').text = genre
    characters_dict[make_id(pair[0])] = [pair[0], pair[1]]

    # revisionDesc
    make_revision()
    # Construct text and body
    SubElement(root, 'text')
    SubElement(text, 'front')
    SubElement(text, 'body')

    return tree


def make_title(title_stmt, title, subtitle):
    if len(subtitle) > 0:
        titlea = SubElement(title_stmt, 'title', type='main')
        titleb = SubElement(title_stmt, 'title', type='sub')
        titleb.text = subtitle
    else:
        titlea = SubElement(title_stmt, 'title')
    titlea.text = title
    return title_stmt


def make_authors(title_stmt, author):
    print(author)
    title_stmt.insert(1, author)
    return title_stmt


def make_editor(title_stmt, editor):
    resp_stmt = SubElement(title_stmt, 'respStmt')
    SubElement(
        resp_stmt,
        'resp').text = 'Automatic generation of the XML/TEI by'
    SubElement(resp_stmt, 'persName').text = editor
    return title_stmt


def make_edition(publication_stmt):
    SubElement(publication_stmt, 'authority').text = authority
    SubElement(publication_stmt, 'publisher').set(
        'xml:id',
        publisher_id).text = publisher
    SubElement(publication_stmt, 'date', when=f'{hodie} {nunc}')
    lic = SubElement(SubElement(publication_stmt, 'availability'), 'licence')
    SubElement(lic, 'ab').text = licence
    SubElement(lic, 'ref').text = licence_url
    return publication_stmt


def make_source(source_stmt, source):
    bibld = SubElement(source_desc, 'bibl').set('type', 'digitalSource')
    source = [x.strip() for x in source.split('*')]
    original = ''
    web = ''
    url = ''
    if len(source) > 0:
        original = source[0]
        if len(source) > 1:
            web = source[1]
            if len(source) > 2:
                url = source[2]
    SubElement(bibld, 'name').text = web
    SubElement(bibld, 'idno').set('type', 'URL').text = url
    biblo = SubElement(source_desc, 'bibl').set('type', 'originalSource')
    SubElement(biblo, 'title').text = original
    SubElement(biblo, 'date', when=date).set('type', 'print')
    SubElement(biblo, 'date', when=date).set('type', 'written')
    return source_stmt


def make_revision():
    first_commit = SubElement(
        SubElement(SubElement(tei_header, 'revisionDesc'),
                   'listChange'), 'change', when=f'{hodie} {nunc}')
    first_commit.text = 'Converted with txt2tei'\
        '<https://github.com/fsanzl/txt2tei>'


def make_participants():
    characters_dict[make_id(pair[0])] = [pair[0], pair[1]]
    list_persons = SubElement(
        SubElement(
            profileDesc,
            'particDesc'),
        'listPerson')
    parse_speakers()


def assign_gender(name):
    if any(x in name for x in '°º'):
        sx = 'MALE'
    elif any(x in name for x in 'ªᵃ'):
        sx = 'FEMALE'
    else:
        name = re.sub(r'(.*)\d.*', '\1', name).strip()
        if any(name.startswith(ambiguous)
               for ambiguous in ['MÚSIC', 'ACOMPAÑAMIENT']):
            sx = 'UNKNOWN'
        elif any(name.endswith(morf) for morf in
                 ['A', 'AS', 'ᵃ', 'ª', 'DOÑA ']):
            sx = 'FEMALE'
        elif any(name.endswith(morf) for morf in
                 ['O', 'OS', '°', 'DON ', 'OR', 'EL', 'UD', 'ÍAS']):
            sx = 'MALE'
        else:
            sx = 'UNKNOWN'
    return sx


def make_id(name):
    name = re.sub(r'(\d)\.[°ªᵃº]', r'\1', name)
    return f'#{unidecode(name.lower().replace(" ", "-"))}'


def find_characters(play_file):
    nombresdf = pd.read_csv('sexos.csv')
    names = []
    characters_dict = {}
    indirect = ['ÉL', 'ELLA', 'ELLOS', 'ELLAS', 'TODOS', 'TODAS']
    #'UNOS', 'OTROS', 'UNAS', 'OTRAS',
    # 'UNO', 'OTRO', 'UNA', 'OTRA']
    collective = ['LOS ', 'LAS ']
    while True:
        line = play_file.readline().split('#')[0]
        if re.search(r'^[\[A-ZÁ-Úa-zá-ú0-9]', line):
            characters = grouped(line)
            for character in characters:
                character = character.strip().replace('[', '').replace(']', '')
                if 'MÚSIC' in character:
                    character = 'MÚSICOS'
                if character not in [item for sublist in [names, indirect]
                                     for item in sublist] and not any(
                                         character.startswith(art)
                                         for art in collective):
                    names.append(character)
        if not line:
            break
    plurals = []
    for name in names:
        name_clean = re.sub(r'(.*)\s+\d.*$', r'\1', name)
        if re.search(r'\d\.*[°ªᵃº]*$', name):
            plurals += [f'{name_clean}{morpheme}'
                        for morpheme in ['S', 'ES']]
    names = [name for name in names if name not in plurals]
    pairs = []
    for name in names:
        name_clean = re.sub(r'(.*)\s+\d.*$', r'\1', name)
        if name_clean in nombresdf['Personaje'].unique():
            sex = nombresdf.loc[nombresdf['Personaje'] ==
                                name_clean].iloc[0]['Sexo']
        else:
            sex = assign_gender(name_clean)
        pairs.append((name, sex))
    for pair in pairs:
        characters_dict[make_id(pair[0])] = [pair[0], pair[1]]
    return characters_dict


def parse_speakers(line):
    collective = ['UNOS', 'OTROS', 'UNAS', 'OTRAS', 'HOMBRES', 'MUJERES',
                  'MÚSIC', 'CORO', 'VOCES', 'SOLDADOS']
    speakers = '<listPerson>'
    for character in line:
        name = line[character][0]
        pid = character.strip('#')
        sex = line[character][1]
        if any([x in name for x in collective]):
            person = 'personGrp'
        else:
            person = 'person'
        char = SubElement(list_person, person).set({'xml:id', pid,
                                                    'sex', sex})
        char.text = name
    return 0


def parse_cast(line):
    characters = line.split('*')
    castlist = '<castList><head>Personajes</head>'
    for character in characters:
        castlist += f'<castItem>{character.strip()}</castItem>'
    return f'{castlist}</castList>'


def compose_profileDesc(speakers_list, genre):
    speakers = parse_speakers(speakers_list)
    return f'<profileDesc><particDesc>{speakers}</particDesc>'\
        f'<textClass><keywords><term type="genreTitle">{genre}</term>'\
        '</keywords></textClass></profileDesc>'


def split_singulars(character, characters_list):
    collective_list = []
    if character.endswith('s'):
        base = character.rstrip('s').rstrip('e')
    for char in characters_list:
        if char.startswith(base) and char != character:
            collective_list.append(char)
    if len(collective_list) < 1:
        collective_list = [character]
    return collective_list


def last_characters(on_stage, character, characters_list):
    if character.endswith('s'):
        collective_list = split_singulars(character, characters_list)
    else:
        collective_list = [character]
    for i in collective_list:
        if i in on_stage:
            on_stage.remove(i)
        on_stage.append(i)
    return on_stage


def grouped(character):
    characters = character.upper().replace(' E ', ' Y '). strip().split(', ')
    return [x.strip() for x in characters[:-1] + characters[-1].split(' Y ')]


def parse_collective_name(character, on_stage, characters_list):
    todos = [
        x for x in on_stage
        if x in characters_list and characters_list[x][1] == 'MALE']
    todas = [
        x for x in on_stage
        if x in characters_list and characters_list[x][1] == 'FEMALE']
    groups = {'TODOS': (-1, False), 'TODAS': (-1, True),
              'LOS DOS': (2, False), 'LOS 2': (2, False), 'ELLOS': (2, False),
              'LAS DOS': (2, True), 'LAS 2': (2, True), 'ELLAS': (2, True),
              'LOS 3': (3, False), 'LOS TRES': (3, False),
              'LAS 3': (3, True), 'LAS TRES': (3, True),
              'LOS 4': (4, False), 'LOS CUATRO': (4, False),
              'LAS 4': (4, True), 'LAS CUATRO': (4, True)}
    if character in groups:
        if not groups[character][1]:
            sex = 'UNKNOWN'
            if all([characters_list[x][1] == 'FEMALE'
                    for x in on_stage[-groups[character][0]:]]):
                collective = todos[-1:] + todas[-groups[character][0] + 1:]
            else:
                sex = 'UNKNOWN'
                collective = on_stage[-groups[character][0]:]
        else:
            sex = 'FEMALE'
            collective = todas[-groups[character][0]:]
    else:
        sex = 'UNKNOWN'
        collective = [x for x in on_stage]
    return collective


def parse_pronoun(pronoun, on_stage, characters_list):
    if pronoun == 'ÉL':
        sex = 'MALE'
    else:
        sex = 'FEMALE'
    return [[person for person in on_stage
             if characters_list[person][1] == sex][-1]]


def parse_exit(on_stage, line):
    line = line.strip().replace('<i>', '')
    if re.search('[Va][n]*se', line, re.IGNORECASE):
        for character in on_stage:
            if character[0] in line.upper():
                on_stage = [x for x in on_stage if x[0] != character[0]]
            elif line.upper().startswith('VASE'):
                on_stage = on_stage[:-1]
            elif line.upper().startswith('VANSE'):
                on_stage = on_stage[:-2]
            else:
                pass
    return on_stage


def parse_speech(ln, nextl, nl):
    attrs = ''
    tabs = ln.count('\t')
    tabsn = nextl.count('\t')
    text = ln.strip()
    if '<p>' in text:
        tag = 'p'
        text = re.search('<p>(.*)', text).group(1)
    else:
        tag = 'l'
        if tabsn > 1:
            if tabs > 1:
                attrs = ' part="M"'
            else:
                attrs = ' part="I"'
        else:
            nl += 1
            if nl % 5 == 0:
                attrs = f' n="{nl}" '
            if tabs > 1:
                attrs += ' part="F"'
    return (f'<{tag}{attrs}>{text}</{tag}>', nl)


def compare_sexes(pids, characters_list):
    return 'UNKNOWN'


def parse_name(ln, characters_list, on_stage):
    sex = ''
    if '#' in ln:
        splitted = ln.split('#')
        ids = splitted[1:]
        speakers = splitted[0].strip().upper()
        pids = [f'#{pid.strip()}' for pid in ids]
        speaker_info = [speakers, pids, '']
        characters_list.append(speaker_info)
    else:
        pids = []
        ip = []
        speakers = ln.upper()
        speakers_list = grouped(speakers)
        for speaker in speakers_list:
            speaker = speaker.replace('[', '').replace(']', '')
            ip = [make_id(speaker)]
            if 'MÚSIC' in speaker:
                ip = ['#musicos']
            # elif ip in characters_list:
            #    speaker_info = [speaker, [ip], characters_list[ip][1]]
            elif any(speaker.startswith(x)
                     for x in ['TODO', 'TODA', 'LOS ', 'LAS ', 'ELLOS', 'ELLAS']):
                ip = parse_collective_name(speaker, on_stage, characters_list)
            elif speaker in ['ÉL', 'ELLA']:
                ip = parse_pronoun(speaker, on_stage, characters_list)
            else:
                pass
            for i in ip:
                if i not in pids:
                    pids.append(i)
        sexos = compare_sexes(pids, characters_list)
        for x in pids:
            on_stage = last_characters(on_stage, x, characters_list)
    ppids = ' '.join(pids)
    return (f'<sp who="{ppids}"><speaker>{speakers}</speaker>', on_stage)


subtitle = ''
source = ''
on_stage = []
dramatis_personae = ''


with open(input_file) as f:
    characters_list = find_characters(f)
with open(input_file) as g:
    lines = g.readlines()
for line in lines:
    if line.startswith('<'):
        label = re.search(r'^<\w*>', line.strip()).group()
        if label in header_labels.keys():
            value = line.strip(f'{label}').strip()
            if label == '<el>':
                dramatis_personae = parse_cast(value)
            else:
                exec(f'{header_labels[label]} = "{value}"')
        else:
            break
    else:
        break

fauthors = parse('authors.xml')
author = author.split()
if len(author) > 1:
    cert = 'medium'
else:
    cert = 'high'
author = author[0]
author = fauthors.xpath(f'//Authors/author[@name="{author}"][@cert="{cert}"]')[0]
print(author)
print(make_tree(title, subtitle, author, source))

licence = licences['cc0']
metadata = [compose_fileDesc(title, subtitle, author, licence, source, date),
            compose_profileDesc(characters_list, genre)]

header = f'<teiHeader>{metadata[0]}{metadata[1]}</teiHeader>'
#############################
preliminaries = f'<front>{dramatis_personae}</front>'
dict_personas = {}

body = ''
other_text = ''
n = 0
act = 0
roman = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
reference = {'1º': 'I', '1.º': 'I', '2º': 'II', '2.º': 'II', '3º': 'III',
             '3.º': 'III', '4º': 'IV', '4.º': 'IV', 'PRIMERO': 'I',
             'SEGUNDO': 'II', 'TERCERO': 'III', 'CUARTO': 'IV',
             '1ª': 'i', '1.ª': 'i', '2ª': 'ii', '2.ª': 'ii', '3ª': 'iii',
             '3.ª': 'iii', '4ª': 'iv', '4.ª': 'iv', 'PRIMERA': 'i',
             'SEGUNDA': 'ii', 'TERCERA': 'iii', 'CUARTA': 'iv'}
speakers_list = []
for idx, line in enumerate(lines):
    body += f'{other_text}'
    other_text = ''
    extra = ''
    changing = False
    next_line = ''
    dive = ''
    cierree = ''
    if not any(line.startswith(x) for x in header_labels):
        changing = False

        if line.startswith('<j>') or line.startswith('<q>'):
            on_stage = []
            div = ''
            if line.startswith('<j>'):
                act += 1
                cierre = cierree
                if act > 1:
                    cierre += '</div>'
                div = f'{cierre}<div type="act" n="{act}"><head>Jornada'\
                    f'{roman[act]}</head>'
                cierree = ''
            else:
                esc += 1
                if esc > 1:
                    cierree = '</div>'
                div = f'{cierree}<div type="scene" n="{esc}"><head>Escena'\
                    f'{esc}</head>'
            body += div

        if line.strip() in reference.keys():
            print(f'{input_file}:\tPlease, edit manually <sp who="#character">'
                  f'for {line.strip()} in {output} verse {n}\n')
        if line.strip().startswith('<i>'):
            body += f'<stage>{line.replace("<i>","").strip()}</stage>'
            parse_exit(speakers_list, line)
        elif re.search(r'^[A-ZÁ-Ú0-9\[\.]+', line):
            parsed_line = parse_name(line, characters_list, on_stage)
            body += parsed_line[0]
            on_stage = parsed_line[1]
        elif line.startswith('\t') or line.startswith('<p>'):
            for i in list(range(1, 9)):
                if idx+i < len(lines):
                    if re.search(r'^[A-ZÁ-Ú0-9\[\.]+', lines[idx+i]):
                        changing = True
                    elif any([x in lines[idx+i] for x in ['<i>', '<x>']]):
                        pass
                    elif lines[idx+i].startswith('\t'):
                        next_line = lines[idx+i]
                        break
                    else:
                        pass
                else:
                    next_line = '\tFinal'
                    changing = True
            parsed_line = parse_speech(line, next_line, n)
            code = parsed_line[0]
            n = parsed_line[1]
            if changing:
                coda = '</sp>'
                changing = False
            else:
                coda = ''
            body += f'{code}{coda}'
document = f'<TEI xmlns="http://www.tei-c.org/ns/1.0">'\
    f'{header}<text xml:lang="es">{preliminaries}<body>{body}'
if act > 1:
    document += '</div>'
document += '</body>'
document += '</text></TEI>'

with open(output, 'w') as output_file:
    output_file.write(BeautifulSoup(document, "xml").prettify())
    # output_file.write(document)
