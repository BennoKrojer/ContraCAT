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


pleonasms_en = ['It was raining', ' It is hard to believe this is true', ' It is a shame',
                ' It seemed this was unnecessary']

pleonasms_de = ['Es regnete', 'Es ist schwer zu glauben, dass das wahr ist', 'Es ist eine Schande',
                'Es schien, dass dies unnötig war']
types = ['rain', 'believe', 'shame', 'seem']

animals = json.load(open('../../templates/entities/animals.json'))
food = json.load(open('../../templates/entities/food.json'))

nom = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
acc = {'m': 'den', 'f': 'die', 'n': 'das'}
dative = {'m': 'dem', 'f': 'der', 'n': 'dem'}

for type, pleo_en, pleo_de in zip(types, pleonasms_en, pleonasms_de):
    path = f'../../templates/2_coreference_step/pleonastic/{type}/'
    os.makedirs(path, exist_ok=True)

    with open(path + 'de_tok', 'w') as tokenized_de, \
            open(path + 'en_tok', 'w') as tokenized_en, \
            open(f'{path}correct', 'w') as correct:
        for a in animals:
            for f in food:
                en_template = f'The {a} ate the {f}. {pleo_en}.'
                en_template = tokenize(en_template, en_tokenizer)
                for _ in range(3):
                    tokenized_en.write(en_template + '\n')
                    correct.write('n\n')

                copy_pleo_de = pleo_de
                a_gender = animals[a]['gender']
                f_gender = food[f]['gender']
                a_de = animals[a]['de']
                f_de = food[f]['de']
                for pron in ['Er', 'Sie', 'Es']:
                    pleo_de = copy_pleo_de.replace('Es', pron)
                    de_template = f'{nom[a_gender]} {a_de} hat {acc[a_gender]} {f_de} gegessen. {pleo_de}.'
                    de_template = tokenize(de_template, de_tokenizer)
                    tokenized_de.write(de_template + '\n')

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}en_tok > {path}en_bpe'
    os.system(command)

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}de_tok > {path}de_bpe'
    os.system(command)

    shutil.copy(os.path.realpath(__file__), f'{path}/generation.py')
