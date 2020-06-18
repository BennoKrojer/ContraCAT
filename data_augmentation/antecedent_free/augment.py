import json

import spacy
from tqdm import tqdm

nlp_de = spacy.load("de_core_news_sm")
gender_conversion = json.load(open('../../resources/german_declination.json'))
gender_pronoun = {'er': 'm','sie':'f','es':'n', 'ihn':'m', 'ihm': 'm'}


def get_new_prev(prev, gender, old_gender, sentence, type='article'):
    if old_gender == gender:
        return prev
    upper = prev[0].isupper()
    old_prev = prev
    prev = prev.lower()

    article = gender_conversion[type].get(prev)
    if list(article.keys())[0] in ['m', 'f', 'n']:
        return article[gender].capitalize() if upper else article[gender]
    else:
        token = [t for t in nlp_de(sentence) if t.text == old_prev][0]
        dep = token.dep_ if type == 'pronoun' else token.head.dep_
        if dep in ['sb', 'sp']:
            case = 'nom'
        elif dep[:2] == 'oa':
            case = 'acc'
        elif dep in ['da', 'op']:
            case = 'dat'
        elif dep in ['og', 'ag']:
            case = 'gen'
        else:
            raise KeyError

        return article[case][gender].capitalize() if upper else article[case][gender]


de = open('de_subtitles', 'r')
en = open('en_subtitles', 'r')
pronouns = open('pronoun_marked', 'r')
alignments = open('alignment', 'r')
indicators = open('indicators', 'r').readlines()


def get_alignment(alignment, idx, sent_de):
    sent_de = sent_de.split(' ')
    for a in alignment.split(' '):
        a = a.strip()
        en, de = a.split('-')
        en, de = int(en), int(de)
        if en == idx:
            if sent_de[de].lower() in gender_conversion['pronoun']:
                return sent_de[de], de


def get_german_variants(sent_en, sent_de, pronoun, alignment, prev_de):
    pronoun_idx = pronoun.split(' ').index('DUMMY_TOKEN')
    res = []
    norm_sent = sent_en.lower().split(' ')
    low_offset = pronoun_idx if pronoun_idx == 0 else pronoun_idx - 1
    pronoun_idx = norm_sent[low_offset:pronoun_idx + 2].index('it') + low_offset
    de_pronoun, de_idx = get_alignment(alignment, pronoun_idx, sent_de)
    modifiy_prev = True if prev_de.lower().split(' ').count(de_pronoun.lower()) == 1 else False
    old_prev_de = prev_de
    for g in ['m', 'f', 'n']:
        if modifiy_prev:
            new_p_prev = get_new_prev(de_pronoun, g, gender_pronoun[de_pronoun.lower()], old_prev_de, type='pronoun')
            tok_old_prev = old_prev_de.split(' ')
            tok_old_prev[old_prev_de.lower().split(' ').index(de_pronoun.lower())] = new_p_prev.capitalize() if \
                de_pronoun[0].isupper() else new_p_prev
            prev_de = ' '.join(tok_old_prev)
            print('WORKED')
        new_p = get_new_prev(de_pronoun, g, gender_pronoun[de_pronoun.lower()], sent_de, type='pronoun')
        tok_sent = sent_de.split(' ')
        tok_sent[de_idx] = new_p
        new_sent = ' '.join(tok_sent)
        res.append((prev_de, new_sent))
    return res


prev_de = de.readline()
prev_en = en.readline()
pronoun_sent = pronouns.readline()
alignment = alignments.readline()

with open('augmentation_antecedent_free_de', 'w') as d, open('augmentation_antecedent_free_en', 'w') as e:
    for i, indicator in tqdm(enumerate(indicators[1:])):
        sent_de = de.readline()
        sent_en = en.readline()
        alignment = alignments.readline()
        pronoun_sent = pronouns.readline()
        if indicator == 'Yes\n':
            try:
                for prev, new in get_german_variants(sent_en, sent_de, pronoun_sent, alignment, prev_de):
                    d.write(prev.strip() + ' <SEP> ' + new.strip() + '\n')
                for _ in range(3):
                    e.write(prev_en.strip() + ' <SEP> ' + sent_en.strip() + '\n')
            except:
                continue

        prev_en = sent_en
        prev_de = sent_de
