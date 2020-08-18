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
overlap = 'verb_overlap'
orders = {'eat_drink_eat': {'en': ('ate', 'drank', 'ate'), 'de': ('gegessen', 'getrunken', 'gegessen')},
          'eat_drink_drink': {'en': ('ate', 'drank', 'drank'), 'de': ('gegessen', 'getrunken', 'getrunken')},
          'drink_eat_eat': {'en': ('drank', 'ate', 'ate'), 'de': ('getrunken', 'gegessen', 'gegessen')},
          'drink_eat_drink': {'en': ('drank', 'ate', 'drank'), 'de': ('getrunken', 'gegessen', 'getrunken')}
          }

nom = {'m': 'der', 'f': 'die', 'n': 'das'}
dat = {'m': 'dem', 'f': 'der', 'n': 'dem'}
acc = {'m': 'den', 'f': 'die', 'n': 'das'}
advs = {'a lot': 'viel', 'quickly': 'schnell', 'slowly': 'langsam', 'happily': 'fröhlich', 'little': 'wenig'}
animals = json.load(open('../../templates/universe/animal.json'))
food = json.load(open('../../templates/universe/food.json'))
drinks = json.load(open('../../templates/universe/drink.json'))

for specification, verbs in orders.items():
    path = f'../../templates/final/2_coreference_step/overlap/{overlap}/{specification}/'
    os.makedirs(path, exist_ok=True)
    with open(path + 'de_tok', 'w') as tokenized_de, \
            open(path + 'en_tok', 'w') as tokenized_en, \
            open(f'{path}/correct', 'w') as correct:
        for a1, a1_de in list(animals.items())[::2]:
            for a2, a2_de in list(animals.items())[::2]:
                # for f, f_de in list(food.items())[::2]:
                #     for d, d_de in list(drinks.items())[::2]:
                for adv, adv_de in advs.items():
                    a1_gender = a1_de['gender']
                    a2_gender = a2_de['gender']
                    if a1_gender != a2_gender:
                        first_correct = True if verbs['en'][0] == verbs['en'][2] else False
                        # x = {'ate': f, 'drank': d}
                        # objs = [x[verbs["en"][0]], x[verbs["en"][1]], x[verbs["en"][2]]]
                        en_template = f'The {a1} {verbs["en"][0]} and the {a2}' \
                                      f' {verbs["en"][1]}. It {verbs["en"][2]} {adv}.'
                        en_template = tokenize(en_template, en_tokenizer)
                        for _ in range(3):
                            tokenized_en.write(en_template + '\n')
                            correct.write((a1_gender if first_correct else a2_gender) + '\n')

                        for pronoun in ['Er', 'Sie', 'Es']:
                            # x = {'gegessen': f_de, 'getrunken': d_de}
                            # objs = [x[verbs["de"][0]], x[verbs["de"][1]], x[verbs["de"][2]]]
                            de_template = f'{nom[a1_de["gender"]].capitalize()} {a1_de["de"]} hat ' \
                                          f'{verbs["de"][0]} und ' \
                                          f'{nom[a2_de["gender"]]} {a2_de["de"]} hat ' \
                                          f'{verbs["de"][1]}. ' \
                                          f'{pronoun} hat {adv_de} {verbs["de"][2]}.'
                            de_template = tokenize(de_template, de_tokenizer)
                            tokenized_de.write(de_template + '\n')

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}en_tok > {path}en_bpe'
    os.system(command)

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}de_tok > {path}de_bpe'
    os.system(command)
    shutil.copy(os.path.realpath(__file__), f'{path}/generation.py')
