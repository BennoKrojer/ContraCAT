import os
from mosestokenizer import MosesTokenizer, MosesPunctuationNormalizer


def combine_nouns(animal_path, people_path):
    ani_nouns = {'m': [], 'f': [], 'n': []}
    people_nouns = {'m': [], 'f': [], 'n': []}
    with open(animal_path, 'r') as ani_file, open(people_path, 'r') as food_file:
        for line in ani_file:
            en, de, gender = line.split(',')
            ani_nouns[gender.strip()].append((en, de))
        for line in food_file:
            en, de, gender = line.split(',')
            people_nouns[gender.strip()].append((en, de))
    pairs = []
    for gender1 in ani_nouns:
        for ani_en, ani_de in ani_nouns[gender1]:
            for gender2 in people_nouns:
                if gender1 != gender2:
                    for food_en, food_de in people_nouns[gender2]:
                        pairs.append(((gender1, ani_en, ani_de), (gender2, food_en, food_de)))

    return pairs


type = '1_entity_step/animal'
first_correct = True
path = f'../../templates_SEP_fixed/{type}/'
os.makedirs(path, exist_ok=True)
pairs = combine_nouns('../../templates_SEP_fixed/animals/nouns', '../../templates_SEP_fixed/1_entity_step/human')
nominative = {'m': 'der', 'f': 'die', 'n': 'das'}


with open(path + 'de_tok', 'w') as tokenized_de, \
        open(path + 'en_tok', 'w') as tokenized_en, \
        MosesPunctuationNormalizer('en') as norm, \
        MosesTokenizer('de') as tok_de, \
        MosesTokenizer('en') as tok_en, \
        open(f'{path}/correct', 'w') as correct:
    for first, second in pairs:
        en_template1 = ' '.join(tok_en(norm(f'The {first[1]} and the {second[1]} come closer. It is looking at '
                                            f'me.')))
        en_template2 = ' '.join(tok_en(norm(f'The {second[1]} and the {first[1]} come closer. It is looking at '
                                            f'me.')))
        en_template1 = en_template1.replace('. ', '. <SEP> ')
        en_template2 = en_template2.replace('. ', '. <SEP> ')
        for _ in range(3):
            tokenized_en.write(en_template1 + '\n')
            correct.write(first[0] + '\n')

        for _ in range(3):
            tokenized_en.write(en_template2 + '\n')
            correct.write(first[0] + '\n')

        for pronoun in ['Er', 'Sie', 'Es']:
            de_phrase = ' '.join(tok_de(norm(f'{nominative[first[0]].capitalize()} {first[2]} und'
                                             f' {nominative[second[0]]} {second[2]} kommen näher. '
                                             f' {pronoun} schaut mich an.')))

            de_phrase = de_phrase.replace('. ', '. <SEP> ')
            tokenized_de.write(de_phrase + '\n')

        for pronoun in ['Er', 'Sie', 'Es']:
            de_phrase = ' '.join(tok_de(norm(f'{nominative[second[0]].capitalize()} {second[2]} und'
                                             f' {nominative[first[0]]} {first[2]} kommen näher. '
                                             f' {pronoun} schaut mich an.')))
            de_phrase = de_phrase.replace('. ', '. <SEP> ')
            tokenized_de.write(de_phrase + '\n')

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}en_tok > {path}en_bpe'
os.system(command)

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}de_tok > {path}de_bpe'
os.system(command)
