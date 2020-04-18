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


de_modification = 'true:'
en_modification = 'true:'
de_path = '../ContraPro_Dario/contrapro.text.tok.prev.de.de'
en_path = '../ContraPro_Dario/contrapro.text.tok.prev.en.en'
output_de = f'../ContraPro_Dario/subtitle_bpe/modified/{de_modification}_de_tok.txt'
output_en = f'../ContraPro_Dario/subtitle_bpe/modified/{en_modification}_en_tok.txt'

with MosesPunctuationNormalizer('de') as norm, MosesTokenizer('de') as tok, MosesDetokenizer('de') as de_tok:
    with open(de_path, 'r') as de_file, open(output_de, 'w') as out:
        for _, line in tqdm(enumerate(de_file)):
            # print(line)
            line = de_tok(line.split())
            context, sent = modify_as_quote(line, 'es ist wahr')
            context, sent = norm(context), norm(sent)
            if context:
                if de_modification == "true:" and context[-1] in string.punctuation:
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
            context, sent = modify_as_quote(line, 'it is true')
            context, sent = norm(context), norm(sent)
            if context:
                if de_modification == "true:" and context[-1] in string.punctuation:
                    context = context[:-2] + context[-1] + context[-2]
                line = ' '.join(tok(context)) + ' <SEP> ' + ' '.join(tok(sent)) + '\n'
                out.write(line)
            else:
                sent = '<SEP> ' + ' '.join(tok(sent)) + '\n'
                out.write(sent)

command_de = f'subword-nmt apply-bpe -c ../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
             f'{output_de} > {output_de.replace("tok", "bpe")}'
command_en = f'subword-nmt apply-bpe -c ../ted_data/train/ende.bpe --glossaries "<SEP>" < {output_en} > ' \
             f'{output_en.replace("tok", "bpe")}'
os.system(command_de)
os.system(command_en)