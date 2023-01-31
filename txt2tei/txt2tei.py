#!/usr/bin/env python3
from libtxt2tei import *
from edition import *
from sys import argv

def main(input_arguments):
    input_file = input_arguments[1]
    output = f'{input_file.rsplit(".", 1)[0]}.xml'
    if len(input_arguments) > 2:
        edition = input_arguments[2]

    with open(input_file) as f:
        characters_list = find_characters(f)
    with open(input_file) as g:
        lines = g.readlines()
    try:
        fauthors = parse('authors.xml')
    except:
        fauthors = False
    for line in lines:
        global author
        global date
        if line.startswith('<'):
            label = re.search(r'^\s*<(\w*)>', line.strip()).group(1)
            if label in header_labels.keys():
                value = line.strip(f'<{label}>').strip()
                variable = f'{header_labels[label]}'
                globals()[variable] = value
            else:
                break
        else:
            break
        if date:
            date = parse_date(date)
        else:
            date = False
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
    tree.write(output, doctype=xml_model, encoding='UTF-8', pretty_print=True)

main(argv)
