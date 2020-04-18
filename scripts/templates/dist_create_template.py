import os

from mosestokenizer import MosesTokenizer, MosesPunctuationNormalizer

nouns = {'m': [], 'f': [], 'n': []}
nominative = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
dativ = {'m': 'dem', 'f': 'der', 'n': 'dem'}

with open('../../templates/distance/nouns', 'r') as file:
    for line in file:
        en, de, gender = line.split(',')
        nouns[gender.strip()].append((en, de))

pairs = []

for m_en,m_de in nouns['m']:
    for f_en,f_de in nouns['f']:
        pairs.append({('m', m_en, m_de), ('f', f_en, f_de)})
    for f_en,f_de in nouns['n']:
        pairs.append({('m', m_en, m_de), ('n', f_en, f_de)})

for m_en,m_de in nouns['f']:
    for f_en,f_de in nouns['n']:
        pairs.append({('f', m_en, m_de), ('n', f_en, f_de)})

with open('../../templates/distance/de_tok', 'w') as tokenized_de, open('../../templates/distance/en_tok', 'w') \
        as tokenized_en, MosesPunctuationNormalizer('en') as norm, MosesTokenizer('de') as tok_de, MosesTokenizer(
    'en') as tok_en, open('../../templates/distance/gender_combination','w') as gender_file:
    for first, second in pairs:
        en_template1 = ' '.join(tok_en(norm(f'The {first[1]} is next to the {second[1]}. I look at it.')))

        en_template2 = ' '.join(tok_en(norm(f'The {second[1]} is next to the {first[1]}. I look at it.')))

        for _ in range(3):
            tokenized_en.write(en_template1 + '\n')
            gender_file.write(first[0]+second[0]+'\n')
        for _ in range(3):
            tokenized_en.write(en_template2 + '\n')
            gender_file.write(second[0] + first[0] + '\n')

        ihn1 = ' '.join(tok_de(norm(f'{nominative[first[0]]} {first[2]} ist neben {dativ[second[0]]} {second[2]}. '
                                    f'Ich schaue ihn an.')))

        tokenized_de.write(ihn1+'\n')
        sie1 = ' '.join(tok_de(norm(f'{nominative[first[0]]} {first[2]} ist neben {dativ[second[0]]} {second[2]}. '
                                    f'Ich schaue sie an.')))

        tokenized_de.write(sie1+'\n')
        es1 = ' '.join(tok_de(norm(f'{nominative[first[0]]} {first[2]} ist neben {dativ[second[0]]} {second[2]}. '
                                    f'Ich schaue es an.')))

        tokenized_de.write(es1+'\n')

        ihn2 = ' '.join(tok_de(norm(f'{nominative[second[0]]} {second[2]} ist neben {dativ[first[0]]} {first[2]}. '
                                    f'Ich schaue ihn an.')))

        tokenized_de.write(ihn2+'\n')
        sie2 = ' '.join(tok_de(norm(f'{nominative[second[0]]} {second[2]} ist neben {dativ[first[0]]} {first[2]}. '
                                    f'Ich schaue sie an.')))

        tokenized_de.write(sie2+'\n')

        es2 = ' '.join(tok_de(norm(f'{nominative[second[0]]} {second[2]} ist neben {dativ[first[0]]} {first[2]}. '
                                   f'Ich schaue es an.')))

        tokenized_de.write(es2+'\n')


command = 'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          '../../templates/distance/en_tok > ../../templates/distance/en_bpe'
os.system(command)

command = 'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
                  '../../templates/distance/de_tok > ../../templates/distance/de_bpe'
os.system(command)