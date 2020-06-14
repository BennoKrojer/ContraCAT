import json
from scripts.utils import get_gender_dict, load_germanet, get_gender
import spacy
import pandas as pd
from tqdm import tqdm
nlp_de = spacy.load("de_core_news_sm")
gender_mapping = get_gender_dict('../resources/dict_cc_original.txt', en_key=False)
_, german_synsets = load_germanet('../GermaNet/GN_V120/GN_V120_XML/nomen*.xml')
gender_conversion = json.load(open('../resources/german_declination.json'))
de_freq = json.load(open('../resources/open_subtitles_de_freq.json', 'r'))


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


def modify(df):
    modified_phrases = dict()
    count_mods = 0
    blacklist = json.load(open('german_synonym_blacklist.json', 'r'))
    for i, row in tqdm(df.iterrows()):
        mods_per_sentence = []
        sentence = row['trg_sent']
        if sentence is not None:
            nouns = get_modifiable_nouns(sentence)
            for prev, noun in nouns:
                if noun in german_synsets:
                    synonyms, head = german_synsets[noun]
                    old_gender = get_gender(gender_mapping, noun, head)
                    synonyms = [syn for syn in synonyms if syn[0] != noun] # only keep synonyms which != original
                    for synonym, head in synonyms:
                        try:
                            if de_freq[synonym.lower()] > 10 and synonym not in blacklist:
                                new_gender = get_gender(gender_mapping, synonym, head)
                                new_prev = get_new_prev(prev, new_gender, old_gender, sentence)
                                sentence = ''.join(sentence)
                                new_sentence = sentence.replace(noun, synonym).replace(prev, new_prev)
                                mods_per_sentence.append(new_sentence)
                                count_mods += 1
                        except:
                            continue
        if mods_per_sentence:
            modified_phrases[sentence] = mods_per_sentence

    json.dump(modified_phrases, open('augmentation_german.json', 'w'), indent=2)
    print(f'{count_mods} sentences modified.')


if __name__ == '__main__':
    df = pd.read_csv('antecedent_aligments', sep='\t')
    modify(df)
