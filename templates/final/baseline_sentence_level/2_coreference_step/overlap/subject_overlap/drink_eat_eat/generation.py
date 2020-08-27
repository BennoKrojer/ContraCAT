import json
import os
import shutil

from mosestokenizer import MosesTokenizer, MosesPunctuationNormalizer

normalizer = MosesPunctuationNormalizer('en')
en_tokenizer = MosesTokenizer('en')
de_tokenizer = MosesTokenizer('de')


def tokenize(sequence, tokenizer):
    res = ' '.join(tokenizer(normalizer(sequence)))
    for punc in ['. ', '? ', '! ']:
        res = res.replace(punc, f'{punc} <SEP> ')
    return res


# parameters:
overlap = 'subject_overlap'
orders = {'eat_drink_eat': {'en': ('ate', 'drank', 'ate'), 'de': ('gegessen', 'getrunken', 'gegessen')},
          'eat_drink_drink': {'en': ('ate', 'drank', 'drank'), 'de': ('gegessen', 'getrunken', 'getrunken')},
          'drink_eat_eat': {'en': ('drank', 'ate', 'ate'), 'de': ('getrunken', 'gegessen', 'gegessen')},
          'drink_eat_drink': {'en': ('drank', 'ate', 'drank'), 'de': ('getrunken', 'gegessen', 'getrunken')}
          }

nom = {'m': 'der', 'f': 'die', 'n': 'das'}
dat = {'m': 'dem', 'f': 'der', 'n': 'dem'}
acc = {'m': 'den', 'f': 'die', 'n': 'das'}
animals = json.load(open('../../templates/vocabulary/animal.json'))
food = json.load(open('../../templates/vocabulary/food.json'))
drinks = json.load(open('../../templates/vocabulary/drink.json'))

for specification, verbs in orders.items():
    path = f'../../templates/final/2_coreference_step/overlap/{overlap}/{specification}/'
    os.makedirs(path, exist_ok=True)
    with open(path + 'de_tok', 'w') as tokenized_de, \
            open(path + 'en_tok', 'w') as tokenized_en, \
            open(f'{path}/correct', 'w') as correct:
        for a1, a1_de in list(animals.items())[::2]:
            for a2, a2_de in list(animals.items())[::2]:
                for f, f_de in list(food.items())[::2]:
                    for d, d_de in list(drinks.items())[::2]:
                        f_gender = f_de['gender']
                        d_gender = d_de['gender']
                        if f_gender != d_gender and a1 != a2:
                            first_correct = True if verbs['en'][0] == verbs['en'][2] else False
                            x = {'ate': f, 'drank': d}
                            objs = [x[verbs["en"][0]], x[verbs["en"][1]], x[verbs["en"][2]]]
                            en_template = f'The {a1} {verbs["en"][0]} the {objs[0]} and the {a2}' \
                                          f' {verbs["en"][1]} the {objs[1]}. The {a1 if first_correct else a2}' \
                                          f' liked it.'
                            en_template = tokenize(en_template, en_tokenizer)
                            for _ in range(3):
                                tokenized_en.write(en_template + '\n')
                                correct.write((f_gender if verbs['en'][2] == 'ate' else d_gender) + '\n')

                            for pronoun in ['ihn', 'sie', 'es']:
                                x = {'gegessen': f_de, 'getrunken': d_de}
                                objs = [x[verbs["de"][0]], x[verbs["de"][1]], x[verbs["de"][2]]]
                                main_subj = a1_de if first_correct else a2_de
                                de_template = f'{nom[a1_de["gender"]].capitalize()} {a1_de["de"]} hat ' \
                                              f'{acc[objs[0]["gender"]]} {objs[0]["de"]} {verbs["de"][0]} und ' \
                                              f'{nom[a2_de["gender"]]} {a2_de["de"]} hat ' \
                                              f'{acc[objs[1]["gender"]]} {objs[1]["de"]} {verbs["de"][1]}. ' \
                                              f'{nom[main_subj["gender"]].capitalize()} {main_subj["de"]} mochte ' \
                                              f'{pronoun}.'
                                de_template = tokenize(de_template, de_tokenizer)
                                tokenized_de.write(de_template + '\n')

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}en_tok > {path}en_bpe'
    os.system(command)

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}de_tok > {path}de_bpe'
    os.system(command)
    shutil.copy(os.path.realpath(__file__), f'{path}/generation.py')
