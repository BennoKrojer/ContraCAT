import os
from mosestokenizer import MosesTokenizer, MosesPunctuationNormalizer

animal_en = ['is hungry', 'is looking around', 'is running around']
animal_de = ['ist hungrig', 'schaut sich um', 'rennt herum']
food_en = ['had a sweet taste', 'had a bitter taste', 'had a sour taste', 'was cooked']
food_de = ['hatte einen süßen Geschmack', 'hatte einen bitteren Geschmack', 'hatte einen sauren Geschmack',
           'war gekocht']
building_en = ['is made out of concrete', 'is made out of wood', 'is being renovated']
building_de = ['ist aus Beton', 'ist aus Holz', 'wird gerade renoviert']
vehicle_en = ['has a broken tire', 'is fast', 'is parked correctly']
vehicle_de = ['hat einen kaputten Reifen', 'ist schnell', 'ist richtig geparkt']


def combine_nouns(animal_path, food_path):
    ani_nouns = {'m': [], 'f': [], 'n': []}
    food_nouns = {'m': [], 'f': [], 'n': []}
    with open(animal_path, 'r') as ani_file, open(food_path, 'r') as food_file:
        for line in ani_file:
            en, de, gender = line.split(',')
            ani_nouns[gender.strip()].append((en, de))
        for line in food_file:
            en, de, gender = line.split(',')
            food_nouns[gender.strip()].append((en, de))
    pairs = []
    for gender1 in ani_nouns:
        for ani_en, ani_de in ani_nouns[gender1]:
            for gender2 in food_nouns:
                if gender1 != gender2:
                    for food_en, food_de in food_nouns[gender2]:
                        pairs.append(((gender1, ani_en, ani_de), (gender2, food_en, food_de)))

    return pairs


type = 'vehicle_building'
path = f'../../templates_SEP_fixed/2_coreference_step/world_knowledge/{type}/'
os.makedirs(path, exist_ok=True)
pairs = combine_nouns('../../templates_SEP_fixed/entity_sets/vehicles', '../../templates_SEP_fixed/entity_sets/buildings')
nominative = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
accusative = {'m': 'den', 'f': 'die', 'n': 'das'}
dative = {'m': 'dem', 'f': 'der', 'n': 'dem'}


with open(path + 'de_tok', 'w') as tokenized_de, \
        open(path + 'en_tok', 'w') as tokenized_en, \
        MosesPunctuationNormalizer('en_full_text') as norm, \
        MosesTokenizer('de_full_text') as tok_de, \
        MosesTokenizer('en_full_text') as tok_en, \
        open(f'../../templates_SEP_fixed/2_coreference_step/world_knowledge/{type}/correct', 'w') as correct:
    for sub, obj in pairs:
        for attr in vehicle_en:
            en_template1 = ' '.join(tok_en(norm(f'The {sub[1]} is in front of the {obj[1]}. It {attr}.')))
            en_template1 = en_template1.replace(' . ', ' . <SEP> ')
            for _ in range(3):
                tokenized_en.write(en_template1 + '\n')
                correct.write(sub[0] + '\n')
        for attr in building_en:
            en_template2 = ' '.join(tok_en(norm(f'The {sub[1]} is in front of the {obj[1]}. It {attr}.')))
            en_template2 = en_template2.replace(' . ', ' . <SEP> ')
            for _ in range(3):
                tokenized_en.write(en_template2 + '\n')
                correct.write(obj[0] + '\n')

        for attr in vehicle_de:
            for pronoun in ['Er', 'Sie', 'Es']:
                de_phrase = ' '.join(tok_de(norm(f'{nominative[sub[0]]} {sub[2]} ist vor {dative[obj[0]]} '
                                                 f'{obj[2]}. {pronoun} {attr}.')))
                de_phrase = de_phrase.replace(' . ', ' . <SEP> ')

                tokenized_de.write(de_phrase + '\n')

        for attr in building_de:
            for pronoun in ['Er', 'Sie', 'Es']:

                de_phrase = ' '.join(tok_de(norm(f'{nominative[sub[0]]} {sub[2]} ist vor {dative[obj[0]]} '
                                                 f'{obj[2]}. {pronoun} {attr}.')))
                de_phrase = de_phrase.replace(' . ', ' . <SEP> ')

                tokenized_de.write(de_phrase + '\n')

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}en_tok > {path}en_bpe'
os.system(command)

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}de_tok > {path}de_bpe'
os.system(command)
