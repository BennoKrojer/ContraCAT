import json
import os
from mosestokenizer import MosesTokenizer, MosesPunctuationNormalizer
import shutil

normalizer = MosesPunctuationNormalizer('en')
en_tokenizer = MosesTokenizer('en')
de_tokenizer = MosesTokenizer('de')


def tokenize(sequence, tokenizer):
    res = ' '.join(tokenizer(normalizer(sequence)))
    for punc in ['. ', '? ', '! ']:
        res = res.replace(punc, f'{punc} <SEP> ')
    return res


nominative = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
dativ = {'m': 'den', 'f': 'die', 'n': 'das'}
acc = {'m': 'dem', 'f': 'der', 'n': 'dem'}
pros = {'m': 'Er', 'f': 'Sie', 'n': 'Es'}
animals = json.load(open('../../templates/entities/animals.json'))
adjectives = json.load(open('../../templates/entities/adjectives_size.json'))
dest = '../../templates/0_priors/position'
os.makedirs(dest, exist_ok=True)

with open(f'{dest}/de_tok', 'w') as tokenized_de, \
        open(f'{dest}/en_tok', 'w') as tokenized_en,\
        open(f'{dest}/gender_combination', 'w') as gender_file:
    for a1 in animals:
        for a2 in animals:
            for a_en, a_de in adjectives.items():
                a1_gender = animals[a1]['gender']
                a2_gender = animals[a2]['gender']
                if a1_gender != a2_gender:
                    en_template = f'I stood in front of the {a1} and the {a2}. It was {a_en}.'
                    en_template = tokenize(en_template, en_tokenizer)

                    for _ in range(3):
                        tokenized_en.write(en_template + '\n')
                        gender_file.write(a1_gender+a2_gender+'\n')

                    for gender, pro in pros.items():
                        de_a1 = animals[a1]['de']
                        de_a2 = animals[a2]['de']
                        de_template = f'Ich stand vor {acc[a1_gender]} {de_a1} und {acc[a2_gender]} {de_a2}. ' \
                                      f'{pro} war {a_de}.'
                        de_template = tokenize(de_template, de_tokenizer)
                        tokenized_de.write(de_template+'\n')

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{dest}/en_tok > {dest}/en_bpe'
os.system(command)

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{dest}/de_tok > {dest}/de_bpe'
os.system(command)
shutil.copy(os.path.realpath(__file__), f'{dest}/generation.py')
normalizer.close()
en_tokenizer.close()
de_tokenizer.close()
