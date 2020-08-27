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


type = '1_entity_step'
first_correct = True
path = f'../../templates/{type}/'
os.makedirs(path, exist_ok=True)
animals = json.load(open('../../templates/vocabulary/animal.json', 'r'))
humans = json.load(open('../../templates/vocabulary/human.json', 'r'))
nom = {'m': 'der', 'f': 'die', 'n': 'das'}
adjs = {'hungry': 'hungrig', 'tired': 'müde', 'happy': 'glücklich', 'nice': 'nett'}
more_en = {'hungry': 'hungrier', 'tired': 'more tired', 'happy': 'happier', 'nice': 'nicer'}
more_de = {'hungrig': 'hungriger', 'müde': 'müder', 'glücklich': 'glücklicher', 'nett': 'netter'}

with open(path + 'de_tok', 'w') as tokenized_de, \
        open(path + 'en_tok', 'w') as tokenized_en, \
        open(f'{path}/correct', 'w') as correct:
    for a in animals:
        for h in humans:
            for h_gender, h_de in humans[h].items():
                a_gender = animals[a]['gender']
                if a_gender != h_gender:
                    for en_adj, de_adj in adjs.items():
                        en_template1 = f'The {a} and the {h} were {en_adj}. However it was {more_en[en_adj]}.'
                        en_template1 = tokenize(en_template1, en_tokenizer)
                        en_template2 = f'The {h} and the {a} were {en_adj}. However it was {more_en[en_adj]}.'
                        en_template2 = tokenize(en_template2, en_tokenizer)
                        for _ in range(3):
                            tokenized_en.write(en_template1 + '\n')
                            correct.write(a_gender + '\n')
                        for _ in range(3):
                            tokenized_en.write(en_template2 + '\n')
                            correct.write(a_gender + '\n')

                        a_de = animals[a]['de']
                        for pronoun in ['er', 'sie', 'es']:
                            de_template = f'{nom[a_gender].capitalize()} {a_de} und {nom[h_gender[0]]} {h_de} waren ' \
                                          f'{de_adj}. Aber {pronoun} war {more_de[de_adj]}.'
                            de_template = tokenize(de_template, de_tokenizer)
                            tokenized_de.write(de_template + '\n')

                        for pronoun in ['er', 'sie', 'es']:
                            de_template = f'{nom[h_gender].capitalize()} {h_de} und {nom[a_gender[0]]} {a_de} waren ' \
                                          f'{de_adj}. Aber {pronoun} war {more_de[de_adj]}.'
                            de_template = tokenize(de_template, de_tokenizer)
                            tokenized_de.write(de_template + '\n')

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}en_tok > {path}en_bpe'
os.system(command)

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}de_tok > {path}de_bpe'
os.system(command)
shutil.copy(os.path.realpath(__file__), f'{path}generation.py')
