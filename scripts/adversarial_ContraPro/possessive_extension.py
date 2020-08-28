import json
import os
import argparse
import config
from collections import defaultdict
from scripts.adversarial_ContraPro.utils import get_word2definite_article, get_sentence_idx
from tqdm import tqdm
import spacy

VALID_POS_SEQS = [['PRP$', 'NN'], ['DT', 'NN'], ['DT', 'NNP'], ['DT', 'JJ', 'NN'], ['DT', 'NN', 'NN'],
                  ['PRP$', 'JJ', 'NN'], ['DT', 'NNP', 'NNP']]
spacy_model = {'en': spacy.load("en_core_web_sm"), 'de': spacy.load("de_core_news_sm")}


def determine_start_index(phrase, ante):
    start_index = 0
    for _ in range(8):
        mid_idx = phrase[start_index + 1:].index(ante[1]) + start_index + 1
        for i in range(mid_idx, -1, -1):
            if ante[0] in phrase[i:mid_idx]:
                return i
        start_index = mid_idx


def get_start_word(word, d):
    if word in d.keys():
        if d[word] == '':
            return word
        else:
            return d[word]
    return None


def _modify(to_be_replaced, to_be_modified, args, lang, word_mapping):
    modified = True
    replacement = args.de if lang == 'de' else args.en
    append = args.de_append if lang == 'de' else args.en_append

    lower_sent, ante = to_be_modified.lower(), [word.lower() for word in to_be_replaced]
    if ante[0] in lower_sent and ante[1] in lower_sent:
        if append:
            starter = get_start_word(ante[0], word_mapping)
            if starter is not None:
                pre_idx = determine_start_index(lower_sent, ante)
                post_idx = lower_sent.index(ante[-1]) + len(ante[-1])
                to_be_modified = to_be_modified[:pre_idx] + starter + ' ' + to_be_modified[pre_idx + len(
                    ante[0]) + 1: post_idx] + ' ' + replacement + to_be_modified[post_idx:]
            else:
                modified = False
        else:
            idx = determine_start_index(lower_sent, ante)
            to_be_modified = to_be_modified[:idx] + replacement + ' ' + to_be_modified[idx + len(ante[0]) + 1:]
    else:
        modified = False

    return to_be_modified, modified


def modify(line, to_be_replaced, ante_distance, args, lang, word_mapping):
    context, sent = line.split('<SEP>')

    if ante_distance == 0:
        sent, modified = _modify(to_be_replaced, sent, args, lang, word_mapping)
    elif ante_distance == 1:
        context, modified = _modify(to_be_replaced, context, args, lang, word_mapping)
    else:
        modified = False

    return context.strip(), sent.strip(), modified


def write_modify(args):
    contrapro = json.load(open(config.contrapro_file, 'r'))
    idx = get_sentence_idx()
    lang2modified_idx = dict()
    lang2modified_examples = dict()

    output = config.adversarial_data_dir / 'possessive_extension' / args.mod_name
    os.makedirs(output, exist_ok=True)
    for lang in ['de', 'en']:
        orignal_lines = open(config.adversarial_data_dir / (lang + '.txt'), 'r').readlines()
        det2def_det = get_word2definite_article(lang)
        modified_idx = set()
        modified_examples = defaultdict(list)
        for example_id, (start, end) in tqdm(enumerate(list(zip(idx, idx[1:])))):
            info = contrapro[example_id]
            ante = info['ref ante phrase'] if lang == "de" else info['src ante phrase']
            dist = info['ante distance']
            if ante is not None:
                pos_tags = [i.tag_ for i in spacy_model['en'](info['src ante phrase'])]
                seq = [i for i in spacy_model[lang](ante)]
                mismatch = False
                if len(pos_tags) != len(seq):
                    mismatch = True

            lines = []
            modified = False
            for i, line in enumerate(orignal_lines[start:end]):
                if ante is None or pos_tags not in VALID_POS_SEQS or mismatch:
                    lines.append('')
                    continue

                context, sent, modified = modify(line, list(map(str, seq)), dist, args, lang, word_mapping=det2def_det)
                if context:
                    line = context + ' <SEP> ' + sent + '\n'
                else:
                    line = '<SEP> ' + sent + '\n'
                if modified:
                    lines.append(line)
                else:
                    break

            if modified:
                modified_idx.add(example_id)
            else:
                lines = [''] * (end - start)
            assert len(lines) == end - start
            for line, original in zip(lines, orignal_lines[start:end]):
                modified_examples[example_id].append((line, original))
        lang2modified_idx[lang] = modified_idx
        lang2modified_examples[lang] = modified_examples

    both_lang_modified_idx = lang2modified_idx['en'] & lang2modified_idx['de']
    print(f"Modified {len(both_lang_modified_idx)} examples out of 12.000")
    with open(output / 'de.txt', 'w') as de_out, open(output / 'en.txt', 'w') as en_out:
        modified_contrapro_subset = []
        idxxx = []
        for i in range(len(idx)):
            if i in both_lang_modified_idx:
                for tuple in lang2modified_examples['de'][i]:
                    de_out.write(tuple[0])
                for tuple in lang2modified_examples['en'][i]:
                    en_out.write(tuple[0])
                modified_contrapro_subset.append(contrapro[i])
                idxxx.append(i)
    with open('../../modified_poss_idx_best_friend', 'w') as f:
        for i in idxxx:
            f.write(str(i)+'\n')

    json.dump(modified_contrapro_subset, open(output / 'modified_contrapro_subset.json', 'w'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mod_name', '-n', help='name of the modification')
    parser.add_argument('--de', '-d', help='German possessive noun phrase to be added to the original antecedent.')
    parser.add_argument('--en', '-e', help='English possessive noun phrase to be added to the original antecedent.')
    parser.add_argument('--de_append', action='store_true', help='If enabled, appends German possessive NP',
                        default=False)
    parser.add_argument('--de_prepend', action='store_true', help='If enabled, prepends German possessive NP',
                        default=False)
    parser.add_argument('--en_append', action='store_true', help='If enabled, appends English possessive NP',
                        default=False)
    parser.add_argument('--en_prepend', action='store_true', help='If enabled, prepends English possessive NP',
                        default=False)
    args = parser.parse_args()
    write_modify(args)
