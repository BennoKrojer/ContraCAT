import os

from mosestokenizer import MosesDetokenizer, MosesPunctuationNormalizer, MosesTokenizer

tokenize = MosesTokenizer('en')
normalize = MosesPunctuationNormalizer('en')
file = open('en_bpe.txt', 'w')
for line in open('en.txt').readlines():
    line = ' '.join(tokenize(normalize(line)))
    line = line.replace('&lt; SEP &gt;', '<SEP>')
    file.write(line+'\n')

command = f'subword-nmt apply-bpe -c ../../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
          f'en_bpe.txt > en_bpe'
os.system(command)
