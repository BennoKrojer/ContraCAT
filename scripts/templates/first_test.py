from mosestokenizer import MosesPunctuationNormalizer, MosesTokenizer

with open('../../templates/He_X_it', 'r') as templates, open('../../templates/de_bpe', 'w') as bpe_de, \
    open('../../templates/en_bpe','w') as bpe_en, MosesPunctuationNormalizer('en') as norm, MosesTokenizer('de') as \
        tok_de, MosesTokenizer('en') as tok_en:

    for line in templates:
        verb_en, verb_de = line.split('-')
        en_template = ' '.join(tok_en(norm(f'He {verb_en} it.')))
        for _ in range(3):
            bpe_en.write(en_template+'\n')

        verb_de = verb_de.split()
        if len(verb_de) == 1:
            ihn = ' '.join(tok_de(norm(f'Er {verb_de[0]} ihn.')))
            bpe_de.write(ihn+'\n')
            sie = ' '.join(tok_de(norm(f'Er {verb_de[0]} sie.')))
            bpe_de.write(sie+'\n')
            es = ' '.join(tok_de(norm(f'Er {verb_de[0]} es.')))
            bpe_de.write(es+'\n')
        else:
            ihn = ' '.join(tok_de(norm(f'Er {verb_de[0]} ihn {verb_de[1]}.')))
            bpe_de.write(ihn+'\n')
            sie = ' '.join(tok_de(norm(f'Er {verb_de[0]} sie {verb_de[1]}.')))
            bpe_de.write(sie+'\n')
            es = ' '.join(tok_de(norm(f'Er {verb_de[0]} es {verb_de[1]}.')))
            bpe_de.write(es+'\n')