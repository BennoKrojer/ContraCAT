import os
import shutil

from mosestokenizer import MosesPunctuationNormalizer, MosesTokenizer

normalizer = MosesPunctuationNormalizer('en')
en_tokenizer = MosesTokenizer('en')
de_tokenizer = MosesTokenizer('de')


def tokenize(sequence, tokenizer):
    res = ' '.join(tokenizer(normalizer(sequence)))
    for punc in ['. ', '? ', '! ']:
        res = res.replace(punc, f'{punc} <SEP> ')
    return res


templates = open('../../templates/entities/He_X_it', 'r').readlines()
subjs = {'I': 'Ich', 'You': 'Du', 'He': 'Er', 'She': 'Sie', 'We': 'Wir', 'They': 'Sie'}
conj = {'I': 'habe', 'You': 'hast', 'He': 'hat', 'She': 'hat', 'We': 'haben', 'They': 'haben'}
dest = '../../templates/0_priors/verb'


with open(f'{dest}/de_tok', 'w') as tokenized_de, open(f'{dest}/en_tok', 'w') as tokenized_en:
    for line in templates:
        for en_subj, de_subj in subjs.items():
            verb_en, verb_de = line.split('-')
            en_template = tokenize(f'Wow! {en_subj} {verb_en} it.', en_tokenizer)
            for _ in range(3):
                tokenized_en.write(en_template + '\n')

            verb_de = verb_de.split()
            if len(verb_de) == 1:
                ihn = tokenize(f'Wow! {de_subj} {verb_de[0]} ihn.', de_tokenizer)
                tokenized_de.write(ihn + '\n')
                sie = tokenize(f'Wow! {de_subj} {verb_de[0]} sie.',de_tokenizer)
                tokenized_de.write(sie + '\n')
                es = tokenize(f'Wow! {de_subj} {verb_de[0]} es.',de_tokenizer)
                tokenized_de.write(es + '\n')
            else:
                verb_de[0] = verb_de[0].replace('hat', conj[en_subj])
                ihn = tokenize(f'Wow! {de_subj} {verb_de[0]} ihn {verb_de[1]}.',de_tokenizer)
                tokenized_de.write(ihn + '\n')
                sie = tokenize(f'Wow! {de_subj} {verb_de[0]} sie {verb_de[1]}.',de_tokenizer)
                tokenized_de.write(sie + '\n')
                es = tokenize(f'Wow! {de_subj} {verb_de[0]} es {verb_de[1]}.',de_tokenizer)
                tokenized_de.write(es + '\n')

command = 'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{dest}/en_tok > {dest}/en_bpe'
os.system(command)

command = 'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'{dest}/de_tok > {dest}/de_bpe'
os.system(command)
shutil.copy(os.path.realpath(__file__), f'{dest}/generation.py')
