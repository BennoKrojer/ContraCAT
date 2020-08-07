from mosestokenizer import MosesDetokenizer

with MosesDetokenizer('de') as detok, open('de_tok.txt', 'w') as en:
    for line in open('de_tok.txt', 'r'):
        line = detok(line.split())
        en.write(line + '\n')
