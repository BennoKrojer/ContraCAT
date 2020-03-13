import os
import string

from mosestokenizer import MosesPunctuationNormalizer, MosesTokenizer, MosesDetokenizer
from tqdm import tqdm


def modify_as_quote(line, prefix):
    context, sent = line.split('<SEP>')
    if not context:
        return '', sent
    context = f'{prefix}: "{context}"'
    return context, sent


def append(line, phrase, new_sentence=False):
    context, sent = line.split('<SEP>')
    context = context.strip()
    if not context:
        return '', sent

    if new_sentence:
        context = context + phrase
    else:
        if context[-1] in string.punctuation:
            context = context[:-1] + phrase + context[-1]
        else:
            context = context + phrase
    return context, sent


de_modification = 'punkt'
en_modification = 'point'
de_path = '../ContraPro_Dario/contrapro.text.tok.prev.de.de'
en_path = '../ContraPro_Dario/contrapro.text.tok.prev.en.en'
output_de = f'../ContraPro_Dario/modified/{de_modification}_de_tok.txt'
output_en = f'../ContraPro_Dario/modified/{en_modification}_en_tok.txt'

with MosesPunctuationNormalizer('de') as norm, MosesTokenizer('de') as tok, MosesDetokenizer('de') as de_tok:
    with open(de_path, 'r') as de_file, open(output_de, 'w') as out:
        for _, line in tqdm(enumerate(de_file)):
            # print(line)
            line = de_tok(line.split())
            context, sent = append(line, ', aber das ist nicht der punkt')
            context, sent = norm(context), norm(sent)
            if context:
                if de_modification == "er_sagte" and context[-1] in string.punctuation:
                    context = context[:-2] + context[-1] + context[-2]
                line = ' '.join(tok(context)) + ' <SEP> ' + ' '.join(tok(sent)) + '\n'
                out.write(line)
            else:
                sent = '<SEP> ' + ' '.join(tok(sent)) + '\n'
                out.write(sent)

with MosesPunctuationNormalizer('en') as norm, MosesTokenizer('en') as tok, MosesDetokenizer('en') as de_tok:
    with open(en_path, 'r') as en_file, open(output_en, 'w') as out:
        for _, line in tqdm(enumerate(en_file)):
            line = de_tok(line.split())
            context, sent = append(line, " but that's not the point")
            context, sent = norm(context), norm(sent)
            if context:
                if de_modification == "er_sagte" and context[-1] in string.punctuation:
                    context = context[:-2] + context[-1] + context[-2]
                line = ' '.join(tok(context)) + ' <SEP> ' + ' '.join(tok(sent)) + '\n'
                out.write(line)
            else:
                sent = '<SEP> ' + ' '.join(tok(sent)) + '\n'
                out.write(sent)

command_de = f'subword-nmt apply-bpe -c ../ted_data/train/ende.bpe --glossaries "<SEP>" < ../ContraPro_Dario/modified/{de_modification}_de_tok.txt > tmp_de.txt'
command_en = f'subword-nmt apply-bpe -c ../ted_data/train/ende.bpe --glossaries "<SEP>" < ../ContraPro_Dario/modified/{en_modification}_en_tok.txt > tmp_en.txt'
os.system(command_de)
os.system(command_en)

with open('tmp_de.txt', 'r') as tmp_de, open(f'../ContraPro_Dario/modified/{de_modification}_de_bpe.txt', 'w') as bpe_de:
    for line in tmp_de:
        bpe_de.write(line)

with open('tmp_en.txt', 'r') as tmp_en, open(f'../ContraPro_Dario/modified/{en_modification}_en_bpe.txt', 'w') as bpe_en:
    for line in tmp_en:
        bpe_en.write(line)

os.system('rm -rf tmp_de.txt')
os.system('rm -rf tmp_en.txt')