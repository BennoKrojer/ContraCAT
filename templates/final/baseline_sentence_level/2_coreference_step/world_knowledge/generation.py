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


animal_en = ['was hungry', 'was looking around', 'was running around', 'was tired', 'was happy']
animal_de = ['war hungrig', 'schaute sich um', 'rannte herum', 'war müde', 'war glücklich']
food_en = ['had a sweet taste', 'had a bitter taste', 'had a sour taste', 'was cooked', 'had gone bad']
food_de = ['hatte einen süßen Geschmack', 'hatte einen bitteren Geschmack', 'hatte einen sauren Geschmack',
           'war gekocht', 'war schlecht geworden']

path = f'../../templates/2_coreference_step/world_knowledge/'
os.makedirs(path, exist_ok=True)
animals = json.load(open('../../templates/vocabulary/animal.json'))
food = json.load(open('../../templates/vocabulary/food.json'))
nominative = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
accusative = {'m': 'den', 'f': 'die', 'n': 'das'}
dative = {'m': 'dem', 'f': 'der', 'n': 'dem'}


with open(path + 'de_tok', 'w') as tokenized_de, \
        open(path + 'en_tok', 'w') as tokenized_en, \
        open(f'{path}/correct', 'w') as correct:
    for a in animals:
        for f in food:
            a_gender = animals[a]['gender']
            f_gender = food[f]['gender']
            if a_gender != f_gender:
                for attr in animal_en:
                    en_template1 = f'The {a} ate the {f}. It {attr}.'
                    en_template1 = tokenize(en_template1, en_tokenizer)
                    for _ in range(3):
                        tokenized_en.write(en_template1 + '\n')
                        correct.write(a_gender + '\n')
                for attr in food_en:
                    en_template1 = f'The {a} ate the {f}. It {attr}.'
                    en_template1 = tokenize(en_template1, en_tokenizer)
                    for _ in range(3):
                        tokenized_en.write(en_template1 + '\n')
                        correct.write(f_gender + '\n')

                a_de = animals[a]['de']
                f_de = food[f]['de']

                for attr in animal_de:
                    for pronoun in ['Er', 'Sie', 'Es']:
                        de_template = f'{nominative[a_gender]} {a_de} hat {accusative[f_gender]} {f_de} gegessen.' \
                                    f' {pronoun} {attr}.'
                        de_template = tokenize(de_template, de_tokenizer)
                        tokenized_de.write(de_template + '\n')
                for attr in food_de:
                    for pronoun in ['Er', 'Sie', 'Es']:
                        de_template = f'{nominative[a_gender]} {a_de} hat {accusative[f_gender]} {f_de} gegessen.' \
                                    f' {pronoun} {attr}.'
                        de_template = tokenize(de_template, de_tokenizer)
                        tokenized_de.write(de_template + '\n')


command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}en_tok > {path}en_bpe'
os.system(command)

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}de_tok > {path}de_bpe'
os.system(command)
shutil.copy(os.path.realpath(__file__), f'{path}/generation.py')
