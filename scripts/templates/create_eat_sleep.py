import os
from mosestokenizer import MosesTokenizer, MosesPunctuationNormalizer

nouns = {'m': [], 'f': [], 'n': []}
nominative = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
dativ = {'m': 'dem', 'f': 'der', 'n': 'dem'}
specification = 'sleep_eat_eat'
with open('../../templates/animals/nouns', 'r') as file:
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

with open(f'../../templates/animals/{specification}/de_tok', 'w') as tokenized_de, \
        open(f'../../templates/animals/{specification}/en_tok','w') as tokenized_en,\
        MosesPunctuationNormalizer('en') as norm,\
        MosesTokenizer('de') as tok_de,\
        MosesTokenizer('en') as tok_en,\
        open(f'../../templates/animals/{specification}/correct', 'w') as correct:

    for first, second in pairs:
        en_template1 = ' '.join(tok_en(norm(f'The {first[1]} is sleeping and the {second[1]} is eating. It is eating '
                                            f'a lot.')))

        en_template2 = ' '.join(tok_en(norm(f'The {second[1]} is sleeping and the {first[1]} is eating. It is eating '
                                            f'a lot.')))

        for _ in range(3):
            tokenized_en.write(en_template1 + '\n')
            correct.write(second[0]+'\n')
        for _ in range(3):
            tokenized_en.write(en_template2 + '\n')
            correct.write(first[0] + '\n')

        ihn1 = ' '.join(tok_de(norm(f'{nominative[first[0]]} {first[2]} schläft und {nominative[second[0]].lower()} '
                                    f'{second[2]} isst. Er isst viel.')))

        tokenized_de.write(ihn1+'\n')
        sie1 = ' '.join(tok_de(norm(f'{nominative[first[0]]} {first[2]} schläft und {nominative[second[0]].lower()} '
                                    f'{second[2]} isst. Sie isst viel.')))

        tokenized_de.write(sie1+'\n')
        es1 = ' '.join(tok_de(norm(f'{nominative[first[0]]} {first[2]} schläft und {nominative[second[0]].lower()} '
                                    f'{second[2]} isst. Es isst viel.')))

        tokenized_de.write(es1+'\n')

        ihn2 = ' '.join(tok_de(norm(f'{nominative[second[0]]} {second[2]} schläft und {nominative[first[0]].lower()} '
                                    f'{first[2]} isst. Er isst viel.')))

        tokenized_de.write(ihn2+'\n')
        sie2 = ' '.join(tok_de(norm(f'{nominative[second[0]]} {second[2]} schläft und {nominative[first[0]].lower()} '
                                    f'{first[2]} isst. Sie isst viel.')))

        tokenized_de.write(sie2+'\n')

        es2 = ' '.join(tok_de(norm(f'{nominative[second[0]]} {second[2]} schläft und {nominative[first[0]].lower()} '
                                    f'{first[2]} isst. Es isst viel.')))
        tokenized_de.write(es2+'\n')


command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'../../templates/animals/{specification}/en_tok > ../../templates/animals/{specification}/en_bpe'
os.system(command)

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
                  f'../../templates/animals/{specification}/de_tok > ../../templates/animals/{specification}/de_bpe'
os.system(command)