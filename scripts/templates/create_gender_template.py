import os

from mosestokenizer import MosesPunctuationNormalizer, MosesTokenizer

from scripts.utils import get_genders

def get_top_german(max=20000):
    top = set()
    with open('../de_50k.txt') as file:
        for line in file.readlines()[:max]:
            top.add(line.split()[0])
    return top


genders = get_genders('../../resources/dict_cc_original.txt')
top_german = get_top_german()

type = 'gender'
path = f'../../templates_SEP_fixed/{type}/'
os.makedirs(path, exist_ok=True)

# new approach:
# 1. extract most frequent nouns from zeit-tagged corpus.
# 2. Get gender from dict-cc
# 3. create templates
with open(path + 'de_tok', 'w') as tokenized_de, \
        open(path + 'en_tok', 'w') as tokenized_en, \
        MosesPunctuationNormalizer('en') as norm, \
        MosesTokenizer('de') as tok_de, \
        MosesTokenizer('en') as tok_en, \
        open(f'../../templates_SEP_fixed/{type}/correct', 'w') as correct:

    for en, (de, gender) in genders.items():
        if de in top_german:
            en_template = f'A {en}? <SEP> I find it interesting.'

            for _ in range(3):
                tokenized_en.write(en_template + '\n')
                correct.write(gender + '\n')
            for (article, pronoun) in [('Ein', 'ihn'), ('Eine', 'sie'), ('Ein', 'es')]:
                de_template = f'{article} {de.capitalize()}? <SEP> Ich finde {pronoun} interessant.'
                tokenized_de.write(de_template + '\n')

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}en_tok > {path}en_bpe'
os.system(command)

command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{path}de_tok > {path}de_bpe'
os.system(command)
