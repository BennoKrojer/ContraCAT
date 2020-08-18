import json
import os
from scripts.adversarial_attack.utils import get_gender_dict

concrete_nouns = [line.rstrip('\n') for line in open('../../resources/concrete_nouns_brysbaert.txt')]
concrete_nouns_de = [line.rstrip('\n') for line in open('../../resources/concrete_nouns_brysbaert_de.txt')]
genders = get_gender_dict('../../resources/dict_cc_original.txt', en_key=False)
de_freq = json.load(open('../../resources/open_subtitles_de_freq.json', 'r'))
en_freq = json.load(open('../../resources/open_subtitles_en_freq.json', 'r'))

# adjs = ['big', 'small', 'large', 'tiny', 'blue', 'red', 'green', 'black', 'white', 'yellow', 'orange']
adjs = ['big', 'small']
# adjs_de = ['groß', 'klein', 'riesig',y', 'blue', 'red', 'green', 'black', 'white', 'yellow', 'orange']
adjs_de = ['groß', 'klein']
for i, type in enumerate(adjs):
    path = f'../../templates/3_gender/{type}/'
    os.makedirs(path, exist_ok=True)

    with open(path + 'de_tok', 'w') as tokenized_de, \
            open(path + 'en_tok', 'w') as tokenized_en, \
            open(f'{path}/correct', 'w') as correct:

        for en, de in zip(concrete_nouns, concrete_nouns_de):
            de = de.capitalize()
            gender = genders.get(de.lower())
            if de in de_freq and de_freq[de] > 30 and en in en_freq and en_freq[en] > 30\
                    and en[-1] != 's' and gender is not None:
                en_template = f'I saw a {en} . <SEP> It was {type} .'

                for _ in range(3):
                    tokenized_en.write(en_template + '\n')
                    correct.write(gender + '\n')
                for (article, pronoun) in [('einen', 'Er'), ('eine', 'Sie'), ('ein', 'Es')]:
                    de_template = f'Ich sah {article} {de} . <SEP> {pronoun} war {adjs_de[i]} .'
                    tokenized_de.write(de_template + '\n')

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}en_tok > {path}en_bpe'
    os.system(command)

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{path}de_tok > {path}de_bpe'
    os.system(command)
