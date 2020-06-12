import json
from scripts.utils import get_gender_dict, load_germanet, get_gender
import spacy
import pandas as pd
from tqdm import tqdm
nlp_de = spacy.load("de_core_news_sm")
gender_mapping = get_gender_dict('../resources/dict_cc_original.txt', en_key=False)
_, german_synsets = load_germanet('../GermaNet/GN_V120/GN_V120_XML/nomen*.xml')
gender_conversion = json.load(open('../resources/gender_conversion.json'))
de_freq = json.load(open('../resources/open_subtitles_de_freq.json', 'r'))

for token in nlp_de('Ich mag sie sehr'):
    print(token.dep_)


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


def get_new_prev(prev, gender, old_gender):
    if prev == '':
        return prev
    if prev.lower() == 'der' and old_gender == 'f':
        return gender_conversion['der_dative'][gender]
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
                    old_gender = get_gender(gender_mapping, noun, head)
                    synonyms = [syn for syn in synonyms if syn[0] != noun] # only keep synonyms which != original
                    for synonym, head in synonyms:
                        try:
                            if de_freq[synonym.lower()] > 10:
                                new_gender = get_gender(gender_mapping, synonym, head)
                                new_prev = get_new_prev(prev, new_gender, old_gender)
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
