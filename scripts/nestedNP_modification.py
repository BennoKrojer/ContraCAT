import json
import os
from collections import defaultdict

from mosestokenizer import MosesPunctuationNormalizer, MosesTokenizer, MosesDetokenizer
from tqdm import tqdm
from scripts.sample_modifications import get_sentence_idx
import spacy
nlp_en = spacy.load("en_core_web_sm")
nlp_de = spacy.load("de_core_news_sm")


def determine_start_index(phrase, ante):
    start_index = 0
    for _ in range(8):
        mid_idx = phrase[start_index+1:].index(ante[1]) + start_index + 1
        for i in range(mid_idx, -1, -1):
            if ante[0] in phrase[i:mid_idx]:
                return i
        start_index = mid_idx


def modify(tokenize, line, to_be_replaced, ante_distance, np, append=True):
    modified = True
    context, sent = line.split('<SEP>')
    # if not context:
    #     return '', ' '.join(tokenize(norm(sent))), modified

    if ante_distance == 0:
        lower_sent, ante = sent.lower(), [word.lower() for word in to_be_replaced]
        if ante[0] in lower_sent and ante[1] in lower_sent:
            if append:
                idx = lower_sent.index(ante) + len(ante)
            else:
                idx = determine_start_index(lower_sent, ante)
            sent = sent[:idx] + ' ' + np + ' ' + sent[idx + len(ante[0])+1:]
        else:
            modified = False
            print('\nAntecedent not found in sentence. Modification not possible\n'
                  f'SENTENCE: {sent}\n'
                  f'MODIFICATION: {to_be_replaced}')

    elif ante_distance == 1:
        lower_context, ante = context.lower(), [word.lower() for word in to_be_replaced]
        if ante[0] in lower_context and ante[1] in lower_context:
            if append:
                idx = lower_context.index(ante) + len(ante)
            else:
                idx = determine_start_index(lower_context, ante)
            context = context[:idx] + ' ' + np + ' ' + context[idx + len(ante[0])+1:]
        else:
            modified = False
            print('\nAntecedent not found in context. Modification not possible\n'
                  f'CONTEXT: {context}\n'
                  f'MODIFICATION: {to_be_replaced}')

    sent = ' '.join(tokenize(norm(sent)))
    if context:
        context = ' '.join(tokenize(norm(context)))
    return context, sent, modified


de_modification = 'david_no_mismatches'
en_modification = 'david_no_mismatches'
de_lines = open('../ContraPro_Dario/contrapro.text.tok.prev.de.de', 'r').readlines()
en_lines = open('../ContraPro_Dario/contrapro.text.tok.prev.en.en', 'r').readlines()
output_de = f'../ContraPro_Dario/modified/{de_modification}_de_tok.txt'
output_en = f'../ContraPro_Dario/modified/{en_modification}_en_tok.txt'
valid_pos_seqs = [['PRP$', 'NN'], ['DT', 'NN'], ['DT', 'NNP'], ['DT', 'JJ', 'NN'], ['DT', 'NN', 'NN'], ['PRP$', 'JJ', 'NN'], ['DT', 'NNP', 'NNP']]


contrapro = json.load(open('../ContraPro/contrapro.json', 'r'))
idx = get_sentence_idx()

modified_count = 0
pos_seqs = defaultdict(list)
modified_idx_de = set()
modified_de = defaultdict(list)
with MosesPunctuationNormalizer('de') as norm, MosesTokenizer('de') as tok, MosesDetokenizer('de') as de_tok:
    for example_id, (start, end) in tqdm(enumerate(list(zip(idx, idx[1:])))):
        info = contrapro[example_id]
        ante = info['ref ante phrase']
        dist = info['ante distance']
        if ante is not None:
            pos_tags = [i.tag_ for i in nlp_en(info['src ante phrase'])]
            seq = [i for i in nlp_de(ante)]
            pos_seqs[str(pos_tags)].append(ante)
            mismatch = False
            if len(pos_tags) != len(seq):
                # print('\nMISMATCH:' + ante)
                mismatch = True

        lines = []
        modified = False
        for i, line in enumerate(de_lines[start:end]):
            if ante is None or pos_tags not in valid_pos_seqs or mismatch:
                lines.append('')
                continue

            line = de_tok(line.split())
            context, sent, modified = modify(tok, line, list(map(str, seq)), dist, 'Davids', append=False)
            if context:
                line = context + ' <SEP> ' + sent + '\n'
            else:
                line = '<SEP> ' + sent + '\n'
            if modified:
                lines.append(line)
            else:
                break

        if modified:
            modified_count += 1
            modified_idx_de.add(example_id)
        else:
            lines = [''] * (end - start)
        assert len(lines) == end - start
        for line, original in zip(lines, de_lines[start:end]):
            modified_de[example_id].append((line, original))

# sorted_pos = sorted(pos_seqs.items(), key=lambda x: len(x[1]), reverse=True)
# humanreadable = '\n'.join([str(len(example)) + '  ' + seq + str(example[:3]) for (seq, example) in sorted_pos])
# print(humanreadable)

modified_count = 0
pos_seqs = defaultdict(list)
mismatch_idx = []
modified_idx_en = set()
modified_en = defaultdict(list)
with MosesPunctuationNormalizer('en') as norm, MosesTokenizer('en') as tok, MosesDetokenizer('en') as de_tok:
    for example_id, (start, end) in tqdm(enumerate(list(zip(idx, idx[1:])))):
        if example_id in mismatch_idx:
            lines.append('')
            continue

        info = contrapro[example_id]
        ante = info['src ante phrase']
        dist = info['ante distance']
        if ante is not None:
            pos_tags = [i.tag_ for i in nlp_en(info['src ante phrase'])]
            seq = [i for i in nlp_en(ante)]
            pos_seqs[str(pos_tags)].append(ante)
            mismatch = False
            if len(pos_tags) != len(seq):
                # print('\nMISMATCH:' + ante)
                mismatch = True

        lines = []
        modified = False
        for i, line in enumerate(en_lines[start:end]):
            if ante is None or pos_tags not in valid_pos_seqs or mismatch:
                lines.append('')
                continue

            line = de_tok(line.split())
            context, sent, modified = modify(tok, line, list(map(str, seq)), dist, "David's", append=False)
            if context:
                line = context + ' <SEP> ' + sent + '\n'
            else:
                line = '<SEP> ' + sent + '\n'
            if modified:
                lines.append(line)
            else:
                break

        if modified:
            modified_count += 1
            modified_idx_en.add(example_id)
        else:
            lines = [''] * (end - start)
        for line, original in zip(lines, en_lines[start:end]):
            modified_en[example_id].append((line, original))


# sorted_pos = sorted(pos_seqs.items(), key=lambda x: len(x[1]), reverse=True)
# humanreadable = '\n'.join([str(len(example)) + '  ' + seq + str(example[:3]) for (seq, example) in sorted_pos])
# print(humanreadable)

both_lang_modified_idx = modified_idx_de & modified_idx_en
print(f"MODIFIED {len(both_lang_modified_idx)} examples out of 12.000")
with open(output_de, 'w') as de_out, open(output_en, 'w') as en_out:
    for i in range(len(idx)):
        if i in both_lang_modified_idx:
            lines_de = [tuple[0] for tuple in modified_de[i]]
            lines_en = [tuple[0] for tuple in modified_en[i]]
        else:
            lines_de = [tuple[1] for tuple in modified_de[i]]
            lines_en = [tuple[1] for tuple in modified_en[i]]
        for de_line, en_line in zip(lines_de, lines_en):
            de_out.write(de_line)
            en_out.write(en_line)

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