import json
import os
import pickle
from collections import defaultdict

from scripts.utils import get_gender_dict, load_germanet, get_gender
import spacy
import pandas as pd
from tqdm import tqdm
nlp_de = spacy.load("de_core_news_sm")
gender_mapping = get_gender_dict('../../resources/dict_cc_original.txt', en_key=False)
_, german_synsets = load_germanet('../../GermaNet/GN_V120/GN_V120_XML/nomen*.xml')
gender_conversion = json.load(open('../../resources/german_declination.json'))
de_freq = json.load(open('../../resources/open_subtitles_de_freq.json', 'r'))
gender_pronoun = {'er': 'm','sie':'f','es':'n', 'ihn':'m', 'ihm': 'm', 'ihr':'f'}


def get_de_ante(row):
    try:
        alignment = row['alignment'].split(',')
        indices = sorted([int(a.split('-')[1]) for a in alignment])
        start, end = indices[0], indices[-1]
        sentence = row['trg_sent'].split()
        return sentence, start, end+1
    except AttributeError:
        return None, None, None


def get_modifiable_nouns(phrase):
    phrase = nlp_de(phrase)
    return [(str(phrase[i-1]) if i != 0 else '', str(phrase[i])) for i in range(len(phrase)) if phrase[i].tag_ == 'NN']


def get_new_prev(prev, gender, old_gender, sentence, type='article', idx=0):
    if prev == '' or gender == old_gender:
        return prev

    else:
        upper = prev[0].isupper()
        old_prev = prev
        prev = prev.lower()

        article = gender_conversion[type].get(prev)
        if list(article.keys())[0] in ['m', 'f', 'n']:
            return article[gender].capitalize() if upper else article[gender]
        else:
            token = [t for t in nlp_de(sentence) if t.text == old_prev][idx]
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
                case = 'nom'

            return article[case][gender].capitalize() if upper else article[case][gender]


def get_alignment(sent_de, gender):
    sent_de = sent_de.split(' ')
    prons = []
    for i, tok in enumerate(sent_de):
        if tok.lower() in gender_conversion['pronoun'] and gender_pronoun[tok.lower()] == gender:
            prons.append((tok, i))
    return prons


def modify_german_main(main_de, new_gender, old_gender):
    try:
        prons = get_alignment(main_de, old_gender)
        new_main_de = main_de
        order = defaultdict(int)
        for pron, idx in prons:
            new_pronoun = get_new_prev(pron, new_gender, old_gender, main_de, type='pronoun', idx=order[pron])
            order[pron] += 1
            tok_sent = new_main_de.split(' ')
            tok_sent[idx] = new_pronoun
            new_main_de = ' '.join(tok_sent)
    except:
        new_main_de = main_de
    return new_main_de

def modify(df):
    count_mods = 0
    blacklist = json.load(open('german_synonym_blacklist.json', 'r'))
    if os.path.exists('cache_modifiable_sentence_ids.pkl'):
        modifiable_sentence_ids = pickle.load(open('cache_modifiable_sentence_ids.pkl','rb'))
        cache_loaded = True
    else:
        modifiable_sentence_ids = []
        cache_loaded = False
    with open('untouched_synonym_de', 'w') as d, open('untouched_synonym_en', 'w') as e:
        for i, row in tqdm(df.iterrows()):
            if not cache_loaded or (cache_loaded and i in modifiable_sentence_ids):
                mods_per_sentence = []
                prev_de = row['trg_sent']
                prev_en = row['src_sent']
                main_de = row['main_trg_sent']
                main_en = row['main_src_sent']
                if prev_de is not None:
                    nouns = get_modifiable_nouns(prev_de)
                    for prev, noun in nouns:
                        if noun in german_synsets:
                            synonyms, head = german_synsets[noun]
                            old_gender = get_gender(gender_mapping, noun, head)
                            synonyms = [syn for syn in synonyms if syn[0] != noun] # only keep synonyms which != original
                            for synonym, head in synonyms:
                                try:
                                    if de_freq[synonym.lower()] > 10 and synonym not in blacklist:
                                        new_gender = get_gender(gender_mapping, synonym, head)
                                        new_prev = get_new_prev(prev, new_gender, old_gender, prev_de)
                                        prev_de = ''.join(prev_de)
                                        new_prev = prev_de.replace(noun, synonym).replace(prev, new_prev)
                                        new_main = modify_german_main(main_de,
                                                                      new_gender, old_gender)
                                        mods_per_sentence.append((new_prev, new_main))
                                        count_mods += 1
                                except:
                                    continue
                if mods_per_sentence:
                    print('!!!')
                    d.write(prev_de.strip() + ' <SEP> ' + main_de.strip() + '\n')
                    e.write(prev_en.strip() + ' <SEP> ' + main_en.strip() + '\n')
                    # for mod_prev, mod_main in mods_per_sentence:
                    #     d.write(mod_prev.strip() + ' <SEP> ' + mod_main.strip() + '\n')
                    #     e.write(prev_en.strip() + ' <SEP> ' + main_en.strip() + '\n')

                    if not cache_loaded:
                        modifiable_sentence_ids.append(i)

        print(f'{count_mods} sentences modified.')
        pickle.dump(modifiable_sentence_ids, open('cache_modifiable_sentence_ids.pkl', 'wb'))


if __name__ == '__main__':
    df = pd.read_csv('alignments', sep='\t')
    modify(df)
