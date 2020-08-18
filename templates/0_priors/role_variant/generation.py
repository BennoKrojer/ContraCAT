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
pros = {'m': 'ihn', 'f': 'sie', 'n': 'es'}
animals = json.load(open('../../templates/universe/animal.json'))
food = json.load(open('../../templates/universe/food.json'))
adjectives = json.load(open('../../templates/universe/size_adjective.json'))
dest = '../../templates/0_priors/role_variant'
os.makedirs(dest, exist_ok=True)
subj = {'He': 'Er', 'She': 'Sie', 'I': 'Ich', 'You': 'Du'}
haben = {'Ich': 'habe', 'Du': 'hast', 'Er': 'hat', 'Sie': 'hat'}

with open(f'{dest}/de_tok', 'w') as tokenized_de, \
        open(f'{dest}/en_tok', 'w') as tokenized_en,\
        open(f'{dest}/gender_combination', 'w') as gender_file:
    for animal in animals:
        for food_entity in food:
            for pro_en, pro_de in subj.items():
                animal_gender = animals[animal]['gender']
                food_gender = food[food_entity]['gender']
                if animal_gender != food_gender:
                    en_template = f'The {animal} ate the {food_entity}. {pro_en} looked at it.'
                    en_template = tokenize(en_template, en_tokenizer)

                    for _ in range(3):
                        tokenized_en.write(en_template + '\n')
                        gender_file.write(animal_gender+food_gender+'\n')

                    for gender, pro in pros.items():
                        de_animal = animals[animal]['de']
                        de_food = food[food_entity]['de']
                        de_template = f'{nominative[animal_gender]} {de_animal} hat {dativ[food_gender]} {de_food} ' \
                                      f'gegessen. {pro_de} ' \
                                      f'{haben[pro_de]} {pro} betrachtet.'
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
