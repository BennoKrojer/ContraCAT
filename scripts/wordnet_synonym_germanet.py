import glob
import json
import re
import spacy
import nltk
from mosestokenizer import MosesDetokenizer
from nltk.corpus import wordnet
import numpy as np
from nltk.wsd import lesk

from scripts.sample_modifications import get_sentence_idx
import xml.etree.ElementTree as ET


nltk.download('wordnet')
nlp_en = spacy.load("en_core_web_sm")
contrapro = json.load(open('../ContraPro/contrapro.json', 'r'))


def load_interlingual():
    root = ET.parse('../GermaNet/GN_V120/GN_V120_XML/interLingualIndex_DE-EN.xml').getroot()
    wn_id2lex_id = dict()
    for entry in root:
        id = entry.attrib['pwn30Id']
        lex_id = entry.attrib['lexUnitId']
        _, offset, pos = id.split('-')
        if pos == 'n' and 'synonym' in entry.attrib['ewnRelation']:
            try:
                wn_id2lex_id[int(offset)] = lex_id
            except ValueError:
                continue
    return wn_id2lex_id


def load_germanet():
    id2synset = dict()
    for filepath in glob.glob('../GermaNet/GN_V120/GN_V120_XML/nomen*.xml'):
        root = ET.parse(filepath).getroot()
        for synset in root:
            # lexs = [orthform.text for lex_unit in synset for orthform in lex_unit if orthform.tag == 'orthForm']
            lexs = []
            for lex_unit in synset:
                head = ''
                for sub in lex_unit:
                    if sub.tag == 'compound':
                        for sub_sub in sub:
                            if sub_sub.tag == 'head':
                                head = sub_sub.text
                for sub in lex_unit:
                    if sub.tag == 'orthForm':
                        lexs.append((sub.text, head))
            ids = {lex_unit.attrib['id']: lexs for lex_unit in synset if lex_unit.tag == "lexUnit"}
            id2synset.update(ids)
    return id2synset


en2lex_id = load_interlingual()
lexid2synset = load_germanet()

def clean_context(context):
    context = context.replace('<SEP> ', '')
    context = MosesDetokenizer('en')(context.split())
    return context


def disambiguate(word, context, synsets):
    if synsets:
        return synsets[0]
    else:
        return None


def get_genders():
    pattern = r'\[.*?\]|\(.*?\)'
    with open('dict_cc_original.txt', 'r') as file:
        genders = dict()
        retrieved = 0
        for line in file:
            if line[0] != '#' and len(line) > 2:
                _, de = line.split(' :: ')
                de = re.sub(pattern, '', de)
                if len(de.split()) == 2:
                    word, gender = de.split()
                    gender = gender.replace('{', '').replace('}', '').strip()
                    if gender in ['m', 'f', 'n']:
                        retrieved += 1
                        genders[word.lower().strip()] = gender
                else:
                    # print(de)
                    pass
        print("!!!!!!!!!!RETRIEVED:" + str(retrieved))
        return genders


de2gender = get_genders()
indices = get_sentence_idx()
context_lines = open('../ContraPro_Dario/contrapro.text.tok.prev.en.en', 'r').readlines()
nn_count = 0
modifiable_count = 0
different_gender_count = 0
for i, example in enumerate(contrapro):
    head = example['src ante head lemma']
    tag = example["src ante head pos"]
    de_head = example['ref ante head lemma']
    context = clean_context(context_lines[indices[i]])
    if 'NN' in tag and de_head is not None:
        nn_count += 1
        synset = disambiguate(head, context, wordnet.synsets(head)) # if it is not ".n" you can ignore it
        if synset:
            id = synset._offset
            try:
                lemma_id = en2lex_id[id]
                german_synset = lexid2synset[lemma_id]
                original_gender = de2gender[de_head.lower()]

                different_gender = False
                german_synonyms = dict()
                for word, head in german_synset:
                    try:
                        if head:
                            gender = de2gender[head.lower()]
                        else:
                            gender = de2gender[word.lower()]
                        german_synonyms[word] = gender
                        if gender != original_gender:
                            different_gender = True
                    except KeyError:
                        continue
                print(f'English antecedent: {head}, German antecedent: {de_head} ({original_gender})')
                print(f'ENGLISH: {synset.lemma_names()}\nGERMAN where gender was identified: {german_synonyms}\n\n')
                modifiable_count += 1
                if different_gender:
                    different_gender_count += 1
            except:
                print(f'{synset} not found\n')

print(f'Found {nn_count} antecedents tagged as NN. {modifiable_count} could be modified right now')
