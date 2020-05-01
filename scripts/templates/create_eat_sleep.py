import os
from mosestokenizer import MosesTokenizer, MosesPunctuationNormalizer


def combine_nouns(noun_file):
    with open(noun_file, 'r') as file:
        for line in file:
            en, de, gender = line.split(',')
            nouns[gender.strip()].append((en, de))
    pairs = []
    for m_en, m_de in nouns['m']:
        for f_en, f_de in nouns['f']:
            pairs.append((('m', m_en, m_de), ('f', f_en, f_de)))
        for f_en, f_de in nouns['n']:
            pairs.append((('m', m_en, m_de), ('n', f_en, f_de)))

    for m_en, m_de in nouns['f']:
        for f_en, f_de in nouns['n']:
            pairs.append((('f', m_en, m_de), ('n', f_en, f_de)))
    return pairs


# parameters:
overlap = 'object_verb_overlap'
specification = 'drink_eat_eat'
first_correct = False
en_template = ['drinking water', 'eating an apple', 'eats the apple quickly']
de_template = ['trinkt Wasser', 'isst einen Apfel', 'isst den Apfel schnell']

nouns = {'m': [], 'f': [], 'n': []}
nominative = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
dative = {'m': 'dem', 'f': 'der', 'n': 'dem'}
path = f'../../templates/animals/{overlap}/{specification}/'
os.makedirs(path, exist_ok=True)
pairs = combine_nouns('../../templates/animals/nouns')

with open(path + 'de_tok', 'w') as tokenized_de, \
        open(path + 'en_tok', 'w') as tokenized_en, \
        MosesPunctuationNormalizer('en') as norm, \
        MosesTokenizer('de') as tok_de, \
        MosesTokenizer('en') as tok_en, \
        open(f'../../templates/animals/{overlap}/{specification}/correct', 'w') as correct:
    for first, second in pairs:
        en_template1 = ' '.join(tok_en(norm(f'The {first[1]} is {en_template[0]} and the {second[1]} is '
                                            f'{en_template[1]}. It is {en_template[2]}.')))

        en_template2 = ' '.join(tok_en(norm(f'The {second[1]} is {en_template[0]} and the {first[1]} is '
                                            f'{en_template[1]}. It is {en_template[2]}.')))
        for _ in range(3):
            tokenized_en.write(en_template1 + '\n')
            correct.write((first[0] if first_correct else second[0]) + '\n')
        for _ in range(3):
            tokenized_en.write(en_template2 + '\n')
            correct.write((first[0] if not first_correct else second[0]) + '\n')

        for pronoun in ['Er', 'Sie', 'Es']:
            de_phrase = ' '.join(tok_de(norm(f'{nominative[first[0]]} {first[2]} {de_template[0]} und'
                                             f' {nominative[second[0]].lower()} {second[2]} {de_template[1]}. {pronoun} '
                                             f'{de_template[2]}.')))

            tokenized_de.write(de_phrase + '\n')

        for pronoun in ['Er', 'Sie', 'Es']:
            de_phrase = ' '.join(tok_de(norm(f'{nominative[second[0]]} {second[2]} {de_template[0]} und'
                                             f' {nominative[first[0]].lower()} {first[2]} {de_template[1]}.'
                                             f' {pronoun} '
                                             f'{de_template[2]}.')))

            tokenized_de.write(de_phrase + '\n')

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}en_tok > {path}en_bpe'
os.system(command)

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}de_tok > {path}de_bpe'
os.system(command)
