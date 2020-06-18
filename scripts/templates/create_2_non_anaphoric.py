import os
from mosestokenizer import MosesTokenizer, MosesPunctuationNormalizer

pleonasms_en = ['It came as a surprise']

pleonasms_de = ['Es kam überraschend']
types = ['surprise']


def combine_nouns(path1, path2):
    nouns = []
    pairs = []
    for path in [path1, path2]:
        with open(path, 'r') as file:
            for line in file:
                en, de, gender = line.split(',')
                nouns.append((gender.strip(), en, de))
    for n1 in nouns:
        for n2 in nouns:
            if n1 != n2:
                pairs.append((n1, n2))

    return pairs


for type, pleo_en, pleo_de in zip(types, pleonasms_en, pleonasms_de):
    path = f'../../templates_SEP_fixed/2_coreference_step/event/{type}/'
    os.makedirs(path, exist_ok=True)
    pairs = combine_nouns('../../templates_SEP_fixed/entity_sets/animals',
                          '../../templates_SEP_fixed/entity_sets/buildings')
    nominative = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
    accusative = {'m': 'den', 'f': 'die', 'n': 'das'}
    dative = {'m': 'dem', 'f': 'der', 'n': 'dem'}

    with open(path + 'de_tok', 'w') as tokenized_de, \
            open(path + 'en_tok', 'w') as tokenized_en, \
            MosesPunctuationNormalizer('en') as norm, \
            MosesTokenizer('de') as tok_de, \
            MosesTokenizer('en') as tok_en, \
            open(f'../../templates_SEP_fixed/2_coreference_step/event/{type}/correct', 'w') as correct:
        for n1, n2 in pairs:
            en_template1 = ' '.join(tok_en(norm(f'The {n1[1]} exploded next to the {n2[1]}. {pleo_en}.')))
            en_template1 = en_template1.replace(' . ', ' . <SEP> ')
            for _ in range(3):
                tokenized_en.write(en_template1 + '\n')
                correct.write('n\n')
            copy_pleo_de = pleo_de
            for nom, dat in [('Er', 'ihn'), ('Sie', 'sie'), ('Es', 'es')]:
                if copy_pleo_de[:2] == 'Es':
                    pleo_de = copy_pleo_de.replace('Es', nom)
                else:
                    pleo_de = copy_pleo_de.replace('es ', dat + ' ')
                de_phrase = ' '.join(tok_de(norm(f'{nominative[n1[0]]} {n1[2]} explodierte neben {dative[n2[0]]} '
                                                 f'{n2[2]}. {pleo_de}.')))
                de_phrase = de_phrase.replace(' . ', ' . <SEP> ')

                tokenized_de.write(de_phrase + '\n')

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}en_tok > {path}en_bpe'
    os.system(command)

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}de_tok > {path}de_bpe'
    os.system(command)
