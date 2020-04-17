import os

from mosestokenizer import MosesPunctuationNormalizer, MosesTokenizer

with open('../../templates/He_X_it', 'r') as templates, open('../../templates/de_tok', 'w') as tokenized_de, \
    open('../../templates/en_tok','w') as tokenized_en, MosesPunctuationNormalizer('en') as norm, MosesTokenizer('de') \
        as \
        tok_de, MosesTokenizer('en') as tok_en:

    for line in templates:
        verb_en, verb_de = line.split('-')
        en_template = ' '.join(tok_en(norm(f'He {verb_en} it.')))
        for _ in range(3):
            tokenized_en.write(en_template + '\n')

        verb_de = verb_de.split()
        if len(verb_de) == 1:
            ihn = ' '.join(tok_de(norm(f'Er {verb_de[0]} ihn.')))
            tokenized_de.write(ihn + '\n')
            sie = ' '.join(tok_de(norm(f'Er {verb_de[0]} sie.')))
            tokenized_de.write(sie + '\n')
            es = ' '.join(tok_de(norm(f'Er {verb_de[0]} es.')))
            tokenized_de.write(es + '\n')
        else:
            ihn = ' '.join(tok_de(norm(f'Er {verb_de[0]} ihn {verb_de[1]}.')))
            tokenized_de.write(ihn + '\n')
            sie = ' '.join(tok_de(norm(f'Er {verb_de[0]} sie {verb_de[1]}.')))
            tokenized_de.write(sie + '\n')
            es = ' '.join(tok_de(norm(f'Er {verb_de[0]} es {verb_de[1]}.')))
            tokenized_de.write(es + '\n')

command = 'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          '../../templates/en_tok > ../../templates/en_bpe'
os.system(command)

command = 'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
                  '../../templates/de_tok > ../../templates/de_bpe'
os.system(command)