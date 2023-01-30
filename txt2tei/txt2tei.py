#!/usr/bin/env python3
from sys import argv
import re
from datetime import datetime
from unidecode import unidecode
import pandas as pd
import lxml.etree as etree
from lxml.etree import Element, SubElement, parse
from config import *

hodie = datetime.today().strftime('%Y-%m-%d')
nunc = datetime.today().strftime('%H:%M:%S')
editor = ''
authority = ''
publisher = ('DraCor', 'dracor', 'https://dracor.org')
licence = 'CC0'
licence_url = 'https://creativecommons.org/publicdomain/zero/1.0/'

xml_model = '<?xml-model href="https://dracor.org/schema.rng" type="applicati'\
    'on/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>'

input_file = argv[1]
output = f'{argv[1].rsplit(".", 1)[0]}.xml'
if len(argv) > 2:
    edition = argv[2]
else:
    edition = '0.1'
header_labels = {'<t>': 'title', '<tt>': 'subtitle', '<a>': 'author',
                 '<g>': 'genre', '<s>': 'subgenre', '<o>': 'source',
                 '<f>': 'date', '<x>': 'comment'}
body_labels = {'j': 'act', '<e>': 'echo', '<p>': 'prose',
               '<i>': 'stage_direction', '<x>': 'comment'}


def make_tree(title, subtitle, author, source, date,
              authority, publisher, licence, speakers_list):
    root = Element('TEI',
                   xmlns='http://www.tei-c.org/ns/1.0')
    root.set('{http://www.w3.org/XML/1998/namespace}lang', 'es')
    tree = etree.ElementTree(root)
    tei_header = SubElement(root, 'teiHeader')
    # fileDesc
    file_desc = SubElement(tei_header, 'fileDesc')
    title_stmt = Element('titleStmt')
    title_stmt = make_title(title_stmt, title, subtitle)
    title_stmt = make_authors(title_stmt, author)
    title_stmt = make_editor(title_stmt, editor)
    file_desc.append(title_stmt)
    # publicationStmt
    publication_stmt = SubElement(file_desc, 'publicationStmt')
    publication_stmt = make_edition(
        publication_stmt, authority, publisher, licence)
    file_desc.append(publication_stmt)
    # srcDesc
    source_desc = SubElement(file_desc, 'sourceDesc')
    make_source(source_desc, source)
    file_desc.append(source_desc)

    # profileDesc
    profile_desc = SubElement(tei_header, 'profileDesc')
    par = SubElement(profile_desc, 'particDesc')
    par.append(make_participants(speakers_list))
    text_class = SubElement(profile_desc, 'textClass')
    gen = SubElement(
        SubElement(
            text_class,
            'keywords'),
        'term',
        type='genreTitle')
    gen.text = genre

    # revisionDesc
    tei_header.append(make_revision())
    # Construct text and body
    standoff = SubElement(root, 'standOff')
    standoff = make_standoff(standoff)

    SubElement(root, 'text')
    return tree


def parse_date(date):
    if '-' in date:
        date = {'notbefore': date.split('-')[0],
                'notafter': date.split('-')[1]}
    elif '?' in date:
        date = {'when': date.strip('?'), 'cert': 'medium'}
    else:
        date = {'when': date, 'cert': 'medium'}
    return date


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
    title_stmt.append(author)
    return title_stmt


def make_editor(title_stmt, editor):
    resp_stmt = SubElement(title_stmt, 'respStmt')
    SubElement(
        resp_stmt,
        'resp').text = 'Automatic generation of the XML/TEI by'
    SubElement(resp_stmt, 'persName').text = editor
    return title_stmt


def make_edition(publication_stmt, authority, publisher, licence):
    SubElement(publication_stmt, 'authority').text = authority
    pub = SubElement(publication_stmt, 'publisher')
    pub.set('{http://www.w3.org/XML/1998/namespace}id', publisher[0])
    pub.text = publisher[1]
    SubElement(publication_stmt, 'idno', type='URL').text = publisher[2]
    SubElement(publication_stmt, 'date', when=f'{hodie}T{nunc}')
    lic = SubElement(SubElement(publication_stmt, 'availability'), 'licence')
    SubElement(lic, 'ab').text = licence
    SubElement(lic, 'ref').text = licence_url
    return publication_stmt


def make_source(source_desc, source):
    bibld = SubElement(source_desc, 'bibl', type='digitalSource')
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
    SubElement(bibld, 'idno', type='URL').text = url
    biblo = SubElement(source_desc, 'bibl', type='originalSource')
    SubElement(biblo, 'title').text = original
    return source_desc


def make_standoff(stand_off):
    list_event = SubElement(stand_off, 'listEvent')
    SubElement(list_event, 'date', date, type='print')
    SubElement(list_event, 'date', date, type='written')
    return stand_off


def make_revision():
    rev = Element('revisionDesc')
    first_commit = SubElement(SubElement(rev, 'listChange'),
                              'change', when=f'{hodie}T{nunc}')
    first_commit.text = 'Converted with txt2tei'\
        '<https://github.com/fsanzl/txt2tei>'
    return rev


def make_participants(speakers_list):
    list_person = Element('listPerson')
    collective = ['UNOS', 'OTROS', 'UNAS', 'OTRAS', 'HOMBRES', 'MUJERES',
                  'MÚSIC', 'CORO', 'VOCES', 'SOLDADOS']
    for character in speakers_list:
        name = speakers_list[character][0]
        pid = character.strip('#')
        sexo = speakers_list[character][1]
        if any([x in name for x in collective]):
            person = 'personGrp'
        else:
            person = 'person'
        char = SubElement(list_person, person, sex=sexo)
        char.set('{http://www.w3.org/XML/1998/namespace}id', pid)
        SubElement(char, 'persName').text = name
    return list_person


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
    # 'UNOS', 'OTROS', 'UNAS', 'OTRAS',
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


def parse_cast(line):
    cast = Element('castList')
    characters = line.split('*')
    if '|' in characters[0]:
        title = characters[0].split('|')
        characters = title[1:] + characters[1:]
        title = title[0]
        SubElement(cast, 'head').text = title
    for character in characters:
        char = character.split(',')
        item = SubElement(cast, 'castItem')
        SubElement(item, 'role').text = char[0]
        if len(char) > 1:
            SubElement(item, 'roleDesc').text = char[1]
    return cast


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
            if all([characters_list[x][1] == 'FEMALE'
                    for x in on_stage[-groups[character][0]:]]):
                collective = todos[-1:] + todas[-groups[character][0] + 1:]
            else:
                collective = on_stage[-groups[character][0]:]
        else:
            collective = todas[-groups[character][0]:]
    else:
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
    tabs = ln.count('\t')
    tabsn = nextl.count('\t')
    text = re.search('(?:<.*>)*(.*)', ln.strip()).group(1)
    if '<p>' in text:
        line = Element('p')
    else:
        line = Element('l')
        if tabsn > 1:
            if tabs > 1:
                line.set('part', 'M')
            else:
                line.set('part', 'I')
        else:
            nl += 1
            if nl % 5 == 0:
                line.set('n', f'{nl}')
            if tabs > 1:
                line.set('part', 'F')
    line.text = text
    return (line, nl)


def compare_sexes(pids, characters_list):
    return 'UNKNOWN'


def parse_name(ln, characters_list, on_stage):
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
            speaker = speaker.strip().replace('[', '').replace(']', '')
            ip = [make_id(speaker)]
            if 'MÚSIC' in speaker:
                ip = ['#musicos']
            # elif ip in characters_list:
            #    speaker_info = [speaker, [ip], characters_list[ip][1]]
            elif any(speaker.startswith(x)
                     for x in ['TODO', 'TODA', 'LOS ', 'LAS ',
                               'ELLOS', 'ELLAS']):
                ip = parse_collective_name(speaker, on_stage, characters_list)
            elif speaker in ['ÉL', 'ELLA']:
                ip = parse_pronoun(speaker, on_stage, characters_list)
            else:
                pass
            for i in ip:
                if i not in pids:
                    pids.append(i)
        for x in pids:
            on_stage = last_characters(on_stage, x, characters_list)
    ppids = ' '.join(pids)
    speech = Element('sp', who=f'{ppids}')
    SubElement(speech, 'speaker').text = speaker
    return (speech, on_stage)


subtitle = ''
source = ''
on_stage = []
dramatis_personae = Element('null')


with open(input_file) as f:
    characters_list = find_characters(f)
with open(input_file) as g:
    lines = g.readlines()
for line in lines:
    if line.startswith('<'):
        label = re.search(r'^<\w*>', line.strip()).group()
        if label in header_labels.keys():
            value = line.strip(f'{label}').strip()
            exec(f'{header_labels[label]} = "{value}"')
        else:
            break
    else:
        break
if date:
    date = parse_date(date)

fauthors = parse('authors.xml')
author = author.split()
if len(author) > 1:
    cert = 'medium'
else:
    cert = 'high'
author = author[0]
authors = [a for a in fauthors.xpath('author')
           if any(b.text == author for b in a.xpath('persName/*'))]
author = [a for a in authors if a.get('cert') == cert][0]
tree = make_tree(
    title,
    subtitle,
    author,
    source,
    date,
    authority,
    publisher,
    licence,
    characters_list)
text = tree.xpath('/TEI/text')[0]
front = SubElement(text, 'front')
body = SubElement(text, 'body')
dict_personas = {}
count = 0
actn = 0
scenen = 1
roman = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
reference = {'1º': 'I', '1.º': 'I', '2º': 'II', '2.º': 'II', '3º': 'III',
             '3.º': 'III', '4º': 'IV', '4.º': 'IV', 'PRIMERO': 'I',
             'SEGUNDO': 'II', 'TERCERO': 'III', 'CUARTO': 'IV',
             '1ª': 'i', '1.ª': 'i', '2ª': 'ii', '2.ª': 'ii', '3ª': 'iii',
             '3.ª': 'iii', '4ª': 'iv', '4.ª': 'iv', 'PRIMERA': 'i',
             'SEGUNDA': 'ii', 'TERCERA': 'iii', 'CUARTA': 'iv'}
speakers_list = []
act = SubElement(body, 'div', type='act', n='1')
scene = SubElement(act, 'div', type='scene', n='1')

for idx, line in enumerate(lines):
    next_line = ''
    if not any(line.startswith(x) for x in header_labels):
        if line.strip() in reference.keys():
            print(f'{input_file}:\tPlease, edit manually <sp who="#character">'
                  f'for {line.strip()} in {output} verse {n}\n')
        if line.startswith('<el>'):
            dramatis_personae = parse_cast(value)
            front.append(dramatis_personae)
        elif line.startswith('<j>') or line.startswith('<q>'):
            on_stage = []
            if line.startswith('<j>'):
                head = line.replace('<j>', '').strip()
                actn += 1
                scenen = 1
                if actn > 1:
                    act = SubElement(body, 'div', type='act', n=f'{actn}')
                    scene = SubElement(act, 'div', type='scene', n=f'{scenen}')
                if head and len(head) > 1:
                    SubElement(act, 'head').text = head
            else:
                scenen += 1
                if scenen > 1:
                    scene = SubElement(act, 'div', type='scene', n=f'{scenen}')
        elif line.strip().startswith('<i>'):
            text = f'{line.replace("<i>","").strip()}'
            if line.startswith('\t'):
                SubElement(sp, 'stage').text = text
            else:
                stage = SubElement(scene, 'stage')
                stage.text = text
                parse_exit(speakers_list, line)
        elif re.search(r'^[A-ZÁ-Ú0-9\[\.]+', line):
            parsed_line = parse_name(line, characters_list, on_stage)
            sp = parsed_line[0]
            scene.append(sp)
            on_stage = parsed_line[1]
        elif line.startswith('\t') or line.strip().startswith('<p>'):
            for i in list(range(1, 9)):
                if idx+i < len(lines):
                    if any([x in lines[idx+i] for x in ['<i>', '<x>']]):
                        pass
                    elif lines[idx+i].startswith('\t'):
                        next_line = lines[idx+i]
                        break
                    else:
                        pass
                else:
                    next_line = '\tFinal'
            parsed_line = parse_speech(line, next_line, count)
            code = parsed_line[0]
            n = parsed_line[1]
            sp.append(code)
tree.write(output, doctype=xml_model, encoding='UTF-8',
           pretty_print=True)
