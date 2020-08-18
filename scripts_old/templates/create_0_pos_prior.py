import json
import os
import config

nominative = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
dativ = {'m': 'den', 'f': 'die', 'n': 'das'}
acc = {'m': 'dem', 'f': 'der', 'n': 'dem'}
pros = {'m': 'Er', 'f': 'Sie', 'n': 'Es'}

animals = json.load(open(config.template_data_dir / 'universe' / 'animal.json'))
adjectives = json.load(open(config.template_data_dir / 'universe' / 'size_adjective.json'))
dest = config.template_data_dir / '0_priors' / 'position'
os.makedirs(dest, exist_ok=True)
sampled = []
with open(dest/'de.txt', 'w') as de_file, \
        open(dest/'en.txt', 'w') as en_file, \
        open(f'{dest}/gender_combination', 'w') as gender_file:
    for a1 in animals:
        for a2 in animals:
            for a_en, a_de in adjectives.items():
                a1_gender = animals[a1]['gender']
                a2_gender = animals[a2]['gender']
                if a1_gender != a2_gender and {a1, a2, a_de} not in sampled:
                    sampled.append({a1, a2, a_de})
                    en_template1 = f'I stood in front of the {a1} and the {a2}. It was {a_en}.'
                    en_template2 = f'I stood in front of the {a2} and the {a1}. It was {a_en}.'
                    en_template1 = tokenize(en_template1, en_tokenizer)
                    en_template2 = tokenize(en_template2, en_tokenizer)

                    for _ in range(3):
                        en_file.write(en_template1 + '\n')
                        gender_file.write(a1_gender + a2_gender + '\n')
                    for _ in range(3):
                        en_file.write(en_template2 + '\n')
                        gender_file.write(a2_gender + a1_gender + '\n')

                    for gender, pro in pros.items():
                        de_a1 = animals[a1]['de']
                        de_a2 = animals[a2]['de']
                        de_template = f'Ich stand vor {acc[a1_gender]} {de_a1} und {acc[a2_gender]} {de_a2}. ' \
                                      f'{pro} war {a_de}.'
                        de_template = tokenize(de_template, de_tokenizer)
                        de.write(de_template + '\n')
                    for gender, pro in pros.items():
                        de_a1 = animals[a1]['de']
                        de_a2 = animals[a2]['de']
                        de_template = f'Ich stand vor {acc[a2_gender]} {de_a2} und {acc[a1_gender]} {de_a1}. ' \
                                      f'{pro} war {a_de}.'
                        de_template = tokenize(de_template, de_tokenizer)
                        de.write(de_template + '\n')
