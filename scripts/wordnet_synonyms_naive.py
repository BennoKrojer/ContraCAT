import json
from collections import defaultdict

import spacy
import nltk
from mosestokenizer import MosesDetokenizer
from nltk.corpus import wordnet
import numpy as np
from scripts.sample_modifications import get_sentence_idx
import re

def get_dict():
    with open('dict_cc_original.txt', 'r') as file:
        translations = []
        for line in file:
            if line[0] != '#' and len(line) > 2:
                en, de = line.split(' :: ')
                translations.append((en, de))
        return translations


nltk.download('wordnet')
nlp_en = spacy.load("en_core_web_sm")
contrapro = json.load(open('../ContraPro/contrapro.json', 'r'))
en2de = get_dict()


def clean_context(context):
    context = context.replace('<SEP> ', '')
    context = MosesDetokenizer('en_full_text')(context.split())
    return context


def disambiguate(word, context, synsets):
    if synsets:
        return synsets[0]
    else:
        return None


def get_translations(en_word):
    possible = [(en, de) for en, de in en2de if en_word in en and '{adj}' not in en and '{adv}' not in en]
    pattern = r'\[.*?\]|\{.*?\}'
    possible = [(re.sub(pattern, '', en), de) for en, de in possible]
    translations = [de.strip() for (en, de) in possible if en.strip().lower() == en_word]
    return translations


indices = get_sentence_idx()
context_lines = open('../ContraPro_Dario/en_tok.txt', 'r').readlines()
nn_count = 0
modifiable_count = 0
for i, example in enumerate(contrapro):
    head = example['src ante head lemma']
    tag = example["src ante head pos"]
    context = clean_context(context_lines[indices[i]])
    if 'NN' in tag:
        nn_count += 1
        # synset = disambiguate(head, context, wordnet.synsets(head))
        translations = defaultdict(int)
        for synset in wordnet.synsets(head):
            if synset:
                synonyms = synset.lemma_names()
                for synonym in synonyms:
                    for translation in get_translations(synonym):
                        translations[translation] += 1

        freq_sort = sorted(translations.items(), key=lambda x:x[1], reverse=True)
        if freq_sort and list(freq_sort)[0][1] > 1:
            print(freq_sort)
            modifiable_count += 1

print(f'Found {nn_count} antecedents tagged as NN. {modifiable_count} could be modified right now')
