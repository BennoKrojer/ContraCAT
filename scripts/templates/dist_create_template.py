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
        pairs.append((('m', m_en, m_de), ('f', f_en, f_de)))
    for f_en,f_de in nouns['n']:
        pairs.append((('m', m_en, m_de), ('n', f_en, f_de)))

for m_en,m_de in nouns['f']:
    for f_en,f_de in nouns['n']:
        pairs.append((('f', m_en, m_de), ('n', f_en, f_de)))

with open('../../templates/distance/and_de_tok', 'w') as tokenized_de, open('../../templates/distance/and_en_tok',
                                                                            'w') \
        as tokenized_en, MosesPunctuationNormalizer('en') as norm, MosesTokenizer('de') as tok_de, MosesTokenizer(
    'en') as tok_en, open('../../templates/distance/gender_combination', 'w') as gender_file:
    for first, second in pairs:
        en_template1 = ' '.join(tok_en(norm(f'I am now standing in front of the {first[1]} and the {second[1]}. I '
                                            f'carefully observe it.')))

        en_template2 = ' '.join(tok_en(norm(f' am now standing in front of the {second[1]} and the {first[1]}. I '
                                            f'carefully look at.')))
        for _ in range(3):
            tokenized_en.write(en_template1 + '\n')
            gender_file.write(first[0]+second[0]+'\n')
        for _ in range(3):
            tokenized_en.write(en_template2 + '\n')
            gender_file.write(second[0] + first[0] + '\n')

        ihn1 = ' '.join(tok_de(norm(f'Ich stehe nun vor {dativ[first[0]]} {first[2]} und {dativ[second[0]]}'
                                    f' {second[2]}. '
                                    f'Ich beobachte ihn sorgfältig.')))

        tokenized_de.write(ihn1+'\n')
        sie1 = ' '.join(tok_de(norm(f'Ich stehe nun vor {dativ[first[0]]} {first[2]} und {dativ[second[0]]}'
                                    f' {second[2]}. '
                                    f'Ich beobachte sie sorgfältig.')))

        tokenized_de.write(sie1+'\n')
        es1 = ' '.join(tok_de(norm(f'Ich stehe nun vor {dativ[first[0]]} {first[2]} und {dativ[second[0]]}'
                                    f' {second[2]}. '
                                    f'Ich beobachte es sorgfältig.')))

        tokenized_de.write(es1+'\n')

        ihn2 = ' '.join(tok_de(norm(f'Ich stehe nun vor {dativ[second[0]]} {second[2]} und {dativ[first[0]]}'
                                    f' {first[2]}. '
                                    f'Ich beobachte ihn sorgfältig.')))
        tokenized_de.write(ihn2+'\n')
        sie2 = ' '.join(tok_de(norm(f'Ich stehe nun vor {dativ[second[0]]} {second[2]} und {dativ[first[0]]}'
                                    f' {first[2]}. '
                                    f'Ich beobachte sie sorgfältig.')))

        tokenized_de.write(sie2+'\n')

        es2 = ' '.join(tok_de(norm(f'Ich stehe nun vor {nominative[second[0]]} {second[2]} und {dativ[first[0]]}'
                                    f' {first[2]}. '
                                    f'Ich beobachte es sorgfältig.')))
        tokenized_de.write(es2+'\n')


command = 'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          '../../templates/distance/and_en_tok > ../../templates/distance/and_en_bpe'
os.system(command)

command = 'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
                  '../../templates/distance/and_de_tok > ../../templates/distance/and_de_bpe'
os.system(command)