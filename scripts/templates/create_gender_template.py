import json
import os

from mosestokenizer import MosesPunctuationNormalizer, MosesTokenizer

from scripts.utils import get_gender_dict


genders = get_gender_dict('../../resources/dict_cc_original.txt')
de_freq = json.load(open('../../resources/open_subtitles_de_freq.json', 'r'))
en_freq = json.load(open('../../resources/open_subtitles_en_freq.json', 'r'))

type = 'gender/gender_talk_a_cleaned'
path = f'../../templates_SEP_fixed/{type}/'
os.makedirs(path, exist_ok=True)

# new approach:
# 1. extract most frequent nouns from training data
# 2. Get gender from dict-cc
# 3. create templates
with open(path + 'de_tok', 'w') as tokenized_de, \
        open(path + 'en_tok', 'w') as tokenized_en, \
        MosesPunctuationNormalizer('en') as norm, \
        MosesTokenizer('de') as tok_de, \
        MosesTokenizer('en') as tok_en, \
        open(f'../../templates_SEP_fixed/{type}/correct', 'w') as correct:

    for en, (de, gender) in genders.items():
        de = de.capitalize()
        if de in de_freq and de_freq[de] > 20 and en in en_freq and en_freq[en] > 20 and en[-1] != 's':
            article = 'an' if en[0] in ['a', 'o', 'e', 'i'] else 'a'
            en_template = f'I mentioned {article} {en}.'

            for _ in range(3):
                tokenized_en.write(en_template + '\n')
                correct.write(gender + '\n')
            for (article, pronoun) in [('einen', 'ihn'), ('eine', 'sie'), ('ein', 'es')]:
                de_template = f'Ich habe {article} {de} erwähnt.'
                tokenized_de.write(de_template + '\n')

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}en_tok > {path}en_bpe'
os.system(command)

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}de_tok > {path}de_bpe'
os.system(command)
