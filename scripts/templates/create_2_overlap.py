import os
from mosestokenizer import MosesTokenizer, MosesPunctuationNormalizer


def combine_nouns(noun_path, food_path, drink_path):
    nouns = {'m': [], 'f': [], 'n': []}
    with open(noun_path, 'r') as noun_file:
        for line in noun_file:
            en, de, gender = line.split(',')
            nouns[gender.strip()].append((en, de))
    pairs = []
    for food in open(food_path, 'r'):
        for drink in open(drink_path, 'r'):
            food_en, food_de, food_gender = food.strip().split(',')
            drink_en, drink_de, drink_gender = drink.strip().split(',')
            for m_en, m_de in nouns['m']:
                for f_en, f_de in nouns['f']:
                    pairs.append((('m', m_en, m_de), ('f', f_en, f_de), (food_gender, food_en, food_de),
                                  (drink_gender, drink_en, drink_de)))
                    pairs.append((('f', f_en, f_de), ('m', m_en, m_de), (food_gender, food_en, food_de),
                                  (drink_gender, drink_en, drink_de)))
                for f_en, f_de in nouns['n']:
                    pairs.append((('m', m_en, m_de), ('n', f_en, f_de), (food_gender, food_en, food_de),
                                  (drink_gender, drink_en, drink_de)))
                    pairs.append((('n', f_en, f_de), ('m', m_en, m_de), (food_gender, food_en, food_de),
                                  (drink_gender, drink_en, drink_de)))

            for m_en, m_de in nouns['f']:
                for f_en, f_de in nouns['n']:
                    pairs.append((('f', m_en, m_de), ('n', f_en, f_de), (food_gender, food_en, food_de),
                                  (drink_gender, drink_en, drink_de)))
                    pairs.append((('n', f_en, f_de), ('f', m_en, m_de), (food_gender, food_en, food_de),
                                  (drink_gender, drink_en, drink_de)))
    return pairs


# parameters:
overlap = 'object_verb_overlap'
orders = {'eat_drink_eat': {'en_full_text': ('eating', 'drinking', 'eating'), 'de_full_text': ('isst', 'trinkt', 'isst')},
          'eat_drink_drink': {'en_full_text': ('eating', 'drinking', 'drinking'), 'de_full_text': ('isst', 'trinkt', 'trinkt')},
          'drink_eat_eat': {'en_full_text': ('drinking', 'eating', 'eating'), 'de_full_text': ('trinkt', 'isst', 'isst')},
          'drink_eat_drink': {'en_full_text': ('drinking', 'eating', 'drinking'), 'de_full_text': ('trinkt', 'isst', 'trinkt')}
          }

nominative = {'m': 'Der', 'f': 'Die', 'n': 'Das'}
dat = {'m': 'dem', 'f': 'der', 'n': 'dem'}
acc = {'m': 'einen', 'f': 'eine', 'n': 'ein'}
acc_det = {'m': 'den', 'f': 'die', 'n': 'das'}
pairs = combine_nouns('../../templates_SEP_fixed/entity_sets/animals', '../../templates_SEP_fixed/entity_sets/food',
                      '../../templates_SEP_fixed/entity_sets/drinks')
for name, verbs in orders.items():
    specification = name
    first_correct = True if verbs['en_full_text'][0] == verbs['en_full_text'][2] else False

    path = f'../../templates_SEP_fixed/2_coreference_step/{overlap}/{specification}/'
    os.makedirs(path, exist_ok=True)

    with open(path + 'de_tok', 'w') as tokenized_de, \
            open(path + 'en_tok', 'w') as tokenized_en, \
            MosesPunctuationNormalizer('en_full_text') as norm, \
            MosesTokenizer('de_full_text') as tok_de, \
            MosesTokenizer('en_full_text') as tok_en, \
            open(f'../../templates_SEP_fixed/2_coreference_step/{overlap}/{specification}/correct', 'w') as correct:

        for a1, a2, food, drink in pairs:
            x = {'eating': food, 'drinking': drink}
            objs = [x[verbs["en_full_text"][0]], x[verbs["en_full_text"][1]], x[verbs["en_full_text"][2]]]
            art_en = ['a' if o is food else '' for o in objs]
            art_de = [acc[food[0]] if o is food else '' for o in objs]
            en_template = f'The {a1[1]} is {verbs["en_full_text"][0]} {art_en[0]} {objs[0][1]} and the {a2[1]} is {verbs["en_full_text"][1]} ' \
                          f'{art_en[1]} {objs[1][1]}. It is {verbs["en_full_text"][2]} the {objs[2][1]} quickly.'
            en_template = ' '.join(tok_en(norm(en_template)))
            en_template = en_template.replace(' . ', ' . <SEP> ')
            for _ in range(3):
                tokenized_en.write(en_template + '\n')
                correct.write((a1[0] if first_correct else a2[0]) + '\n')

            for pronoun in ['Er', 'Sie', 'Es']:
                de_template = f'{nominative[a1[0]]} {a1[2]} {verbs["de_full_text"][0]} {art_de[0]} {objs[0][2]} und ' \
                              f'{nominative[a2[0]].lower()} {a2[2]} {verbs["de_full_text"][1]} {art_de[1]} {objs[1][2]}. ' \
                              f'{pronoun} {verbs["de_full_text"][2]} {acc_det[objs[2][0]]} {objs[2][2]} schnell. '
                de_template = ' '.join(tok_de(norm(de_template)))
                de_template = de_template.replace(' . ', ' . <SEP> ')
                tokenized_de.write(de_template + '\n')

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}en_tok > {path}en_bpe'
    os.system(command)

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}de_tok > {path}de_bpe'
    os.system(command)
