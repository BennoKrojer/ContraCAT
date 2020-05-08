import os
from mosestokenizer import MosesTokenizer, MosesPunctuationNormalizer


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


type = 'animacy/fressen'
first_correct = True
path = f'../../templates/animals/{type}/'
os.makedirs(path, exist_ok=True)
pairs = combine_nouns('../../templates/animals/nouns', '../../templates/animals/food')
nominative = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
accusative = {'m': 'den', 'f': 'die', 'n': 'das'}


with open(path + 'de_tok', 'w') as tokenized_de, \
        open(path + 'en_tok', 'w') as tokenized_en, \
        MosesPunctuationNormalizer('en') as norm, \
        MosesTokenizer('de') as tok_de, \
        MosesTokenizer('en') as tok_en, \
        open(f'../../templates/animals/{type}/correct', 'w') as correct:
    for first, second in pairs:
        en_template1 = ' '.join(tok_en(norm(f'The {first[1]} was eating the {second[1]}. It was hungry.')))
        en_template2 = ' '.join(tok_en(norm(f'The {first[1]} was eating the {second[1]}. It was delicious.')))

        for _ in range(3):
            tokenized_en.write(en_template1 + '\n')
            correct.write((first[0] if first_correct else second[0]) + '\n')
        for _ in range(3):
            tokenized_en.write(en_template2 + '\n')
            correct.write((first[0] if not first_correct else second[0]) + '\n')

        for pronoun in ['Er', 'Sie', 'Es']:
            de_phrase = ' '.join(tok_de(norm(f'{nominative[first[0]]} {first[2]} hat {accusative[second[0]]} '
                                             f'{second[2]} gefressen. {pronoun} war hungrig.')))

            tokenized_de.write(de_phrase + '\n')

        for pronoun in ['Er', 'Sie', 'Es']:
            de_phrase = ' '.join(tok_de(norm(f'{nominative[first[0]]} {first[2]} hat {accusative[second[0]]} '
                                             f'{second[2]} gefressen. {pronoun} war lecker.')))

            tokenized_de.write(de_phrase + '\n')

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}en_tok > {path}en_bpe'
os.system(command)

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}de_tok > {path}de_bpe'
os.system(command)
