#!/usr/bin/env python3
from sys import argv
import re
from unidecode import unidecode
from  sys import stdin
inputfile = argv[1]


def grouped(character):
    characters = character.upper().replace(' E ', ' Y '). strip().split(', ')
    return [x.strip() for x in characters[:-1] +
            characters[-1].split(' Y ')]


def sexa(nombre):
    if any(nombre.startswith(ambiguo)
           for ambiguo in ['MÚSIC', 'ACOMPAÑAMIENT']):
        sx = 'UNKNOWN'
    elif nombre.startswith('DOÑÁ '):
        sx = 'FEMALE'
    elif nombre.startswith('DON '):
        sx = 'MALE'
    elif any(nombre.endswith(morf) for morf in
             ['A', 'ᵃ', 'ª', 'IZ', 'DAD', 'UD']):
        sx = 'FEMALE'
    elif any(nombre.endswith(morf) for morf in
             ['O', 'OS', '°', 'OR', 'EL', 'ÍAS']):
        sx = 'MALE'
    else:
        sx = 'UNKNOWN'
    return sx


lista = []
with open(inputfile) as f:
    lines = f.readlines()

for line in lines:
    line = line.strip()
    personajes = grouped(line)
    for personaje in personajes:
        nombre = re.sub(r'(.*)\d.*', '\1', personaje).strip()
        if [nombre, 'UNKNOWN'] not in lista:
            lista.append([nombre, 'UNKNOWN'])


indirectos = ['ÉL', 'ELLA', 'ELLOS', 'ELLAS',
              'TODOS', 'TODAS',
              'UNOS', 'OTROS', 'UNAS', 'OTRAS', 'UNO', 'OTRO', 'UNA', 'OTRA']
colectivos = ['LOS', 'LAS']



for idx, nombre in enumerate(lista):
    lista[idx][1] = sexa(lista[idx][0])
    variable = input(f'{nombre}\t{sexa(lista[idx][0])}\n')
    if len(variable) > 0:
        if variable == 'm':
            lista[idx][1] = 'MALE'
        elif variable == 'f':
            lista[idx][1] = 'FEMALE'
        elif variable == 'q':
            break
        else:
            lista[idx][1] = 'UNKNOWN'
texto =''
for i in lista:
    texto += f'{i[0]},{i[1]}\n'

with open('salida.lst', 'w') as output_file:
     output_file.write(texto)
