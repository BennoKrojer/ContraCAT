import json
from collections import defaultdict

import spacy
nlp_de = spacy.load("de_core_news_sm")
gender_conversion = json.load(open('../resources/german_declination.json'))


def get_new_prev(prev, gender, old_gender, sentence):

    if prev == '' or gender == old_gender:
        return prev

    else:
        upper = prev.isupper()
        old_prev = prev
        prev = prev.lower()

        article = gender_conversion['article'].get(prev)
        if list(article.keys())[0] in ['m', 'f', 'n']:
            return article[gender].capitalize() if upper else article[gender]
        else:
            token = [t for t in nlp_de(sentence) if t.text == old_prev][0]
            head_dep = token.head.dep_
            if head_dep in ['sb', 'sp']:
                case = 'nom'
            elif head_dep[:2] == 'oa':
                case = 'acc'
            elif head_dep in ['da', 'op']:
                case = 'dat'
            elif head_dep in ['og', 'ag']:
                case = 'gen'
            else:
                raise KeyError

            return article[case][gender].capitalize() if upper else article[case][gender]


de = open('antecedent_free/OpenSubtitles.de-en.clean.train.tok.de.mod_for_coref','r')
en = open('antecedent_free/OpenSubtitles.de-en.clean.train.tok.en.mod_for_coref','r')
indicators = open('antecedent_free/it-indicators-new-final.txt','r').readlines()
counts = defaultdict(int)

prev_de = de.readline()
prev_en = en.readline()
with open('augmentation_antecedent_free_de', 'w') as d, open('augmentation_antecedent_free_en', 'w') as e:
    for i, indicator in enumerate(indicators[1:]):
        sent_de = de.readline()
        sent_en = en.readline()
        if indicator == 'Yes\n':
            er = sent_de.lower().split(' ').count('er')
            sie = sent_de.lower().split(' ').count('sie')
            es = sent_de.lower().split(' ').count('es')
            er1 = prev_de.lower().split(' ').count('er')
            sie1 = prev_de.lower().split(' ').count('sie')
            es1 = prev_de.lower().split(' ').count('es')
            counts[f'er{str(er1)}sie{str(sie1)}es{str(es1)}_er{str(er)}sie{str(sie)}es{str(es)}'] += 1
            # if {'er', 'sie', 'es'} & set(sent_de.lower().split(' ')) == 1:
            d.write(prev_de.strip() + ' <SEP> ' + sent_de.strip()+'\n')
            e.write(prev_en.strip() + ' <SEP> ' + sent_en.strip()+'\n')

        prev_en = sent_en
        prev_de = sent_de
print(sorted(counts.items(), key=lambda x: x[1], reverse=True))