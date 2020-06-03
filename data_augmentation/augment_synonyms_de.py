import json

from scripts.utils import get_genders, load_germanet
import spacy
import pandas as pd
from tqdm import tqdm
nlp_de = spacy.load("de_core_news_sm")
gender_mapping = get_genders('../resources/dict_cc_original.txt', en_key=False)
_, german_synsets = load_germanet('../GermaNet/GN_V120/GN_V120_XML/nomen*.xml')
gender_conversion = json.load(open('../resources/gender_conversion.json'))


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


def get_new_prev(prev, gender):
    if prev == '':
        return prev
    else:
        if prev[0].isupper():
            return gender_conversion.get(prev.lower()).get(gender).capitalize()
        else:
            return gender_conversion.get(prev).get(gender)


def modify(df):
    modified_phrases = dict()
    count_mods = 0
    for i, row in tqdm(df.iterrows()):
        mods_per_sentence = []
        sentence = row['trg_sent']
        if sentence is not None:
            nouns = get_modifiable_nouns(sentence)
            for prev, noun in nouns:
                if noun in german_synsets:
                    synonyms, head = german_synsets[noun]
                    synonyms = [syn for syn in synonyms if syn[0] != noun] # only keep synonyms which != original
                    for synonym, head in synonyms:
                        try:
                            new_gender = gender_mapping[head.lower()] if head else gender_mapping[synonym.lower()]

                            new_prev = get_new_prev(prev, new_gender)
                            sentence = ''.join(sentence)
                            new_sentence = sentence.replace(noun, synonym).replace(prev, new_prev)
                            mods_per_sentence.append(new_sentence)
                            count_mods += 1
                            print(f'{count_mods} sentences modified so far.')
                        except:
                            continue
        if mods_per_sentence:
            modified_phrases[sentence] = mods_per_sentence

    json.dump(modified_phrases, open('augmentation_german.json', 'w'), indent=2)


if __name__ == '__main__':
    df = pd.read_csv('antecedent_aligments', sep='\t')
    modify(df)
