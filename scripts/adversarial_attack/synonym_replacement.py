import glob
import json
import os
import pickle
import shutil
from collections import defaultdict
import nltk
import tqdm
from mosestokenizer import MosesDetokenizer, MosesPunctuationNormalizer, MosesTokenizer
from nltk.corpus import wordnet
import xml.etree.ElementTree as ET
from scripts.utils import get_gender_dict, get_word2definite_article, get_sentence_idx
import config

nltk.download('wordnet')


def load_interlingual():
    root = ET.parse(config.resources_dir / 'GermaNet/GN_V120/GN_V120_XML/interLingualIndex_DE-EN.xml').getroot()
    wn_id2lex_id = dict()
    for entry in root:
        id = entry.attrib['pwn30Id']
        lex_id = entry.attrib['lexUnitId']
        _, offset, pos = id.split('-')
        if pos == 'n' and 'synonym' in entry.attrib['ewnRelation']:
            try:
                wn_id2lex_id[int(offset)] = lex_id
            except ValueError:
                continue
    return wn_id2lex_id


def load_germanet():
    id2synset = dict()
    for filepath in glob.glob(str(config.resources_dir / 'GermaNet/GN_V120/GN_V120_XML/nomen*.xml')):
        root = ET.parse(filepath).getroot()
        for synset in root:
            # lexs = [orthform.text for lex_unit in synset for orthform in lex_unit if orthform.tag == 'orthForm']
            lexs = []
            for lex_unit in synset:
                head = ''
                for sub in lex_unit:
                    if sub.tag == 'compound':
                        for sub_sub in sub:
                            if sub_sub.tag == 'head':
                                head = sub_sub.text
                for sub in lex_unit:
                    if sub.tag == 'orthForm':
                        lexs.append((sub.text, head))
            ids = {lex_unit.attrib['id']: lexs for lex_unit in synset if lex_unit.tag == "lexUnit"}
            id2synset.update(ids)
    return id2synset


en2lex_id = load_interlingual()
lexid2synset = load_germanet()


def clean_context(context):
    context = context.replace('<SEP> ', '')
    context = context.split()
    return context


def disambiguate(word, context, synsets):
    if synsets:
        return synsets[0]
    else:
        return None


results = []
de2gender = get_gender_dict(config.resources_dir / 'dict_cc_original.txt', en_key=False)
indices = get_sentence_idx()
en_context_lines = open(config.adversarial_data_dir / 'en.txt', 'r').readlines()
de_context_lines = open(config.adversarial_data_dir / 'de.txt', 'r').readlines()
modifications_file = open('possible_modifications', 'w')

modification_name = 'male'
en_lines = open(config.adversarial_data_dir / 'en.txt', 'r').readlines()
de_lines = open(config.adversarial_data_dir / 'de.txt', 'r').readlines()
output_de = config.adversarial_data_dir / 'synonyms' / 'male'
output_en = config.adversarial_data_dir / 'synonyms' / 'male'

det2def_det = get_word2definite_article('de')
gender_change = json.load(open(config.resources_dir / 'gender_conversion.json'))
contrapro = json.load(open(config.contrapro_file, 'r'))
idx = get_sentence_idx()

modified = False
modified_indices = []
modified_idx_de = set()
modified_de = defaultdict(list)
to_be_examined = ""
count_preword = defaultdict(int)
with MosesPunctuationNormalizer('de') as norm, MosesTokenizer('de') as tok, MosesDetokenizer(
        'de') as de_tok, \
        open(output_de / 'de.txt', 'w') as de_file:
    for i, example in tqdm.tqdm(enumerate(contrapro)):
        head = example['src ante head lemma']
        tag = example["src ante head pos"]
        de_head = example['ref ante head lemma']
        dist = example['ante distance']
        en_context = clean_context(en_context_lines[indices[i]])
        de_context = clean_context(de_context_lines[indices[i]])
        if 'NN' in tag and de_head and dist < 2 and (
                de_head in tok(de_context_lines[indices[i]]) or de_head in de_context):
            synset = disambiguate(head, en_context, wordnet.synsets(head))  # if it is not ".n" you can ignore it
            if synset:
                id = synset._offset
                try:
                    lemma_id = en2lex_id[id]
                    german_synset = lexid2synset[lemma_id]
                    original_gender = de2gender[de_head.lower()]
                    different_gender = False
                    german_synonyms = dict()
                    gender_instance = []
                    for word, compound_head in german_synset:
                        try:
                            if compound_head:
                                gender = de2gender[compound_head.lower()]
                            else:
                                gender = de2gender[word.lower()]
                            german_synonyms[word] = gender
                            if gender != original_gender:
                                different_gender = True
                                if gender == 'm' and word.lower() != de_head.lower():
                                    gender_instance.append(word)
                        except KeyError:
                            continue

                    if gender_instance:
                        for j, line in enumerate(de_lines[indices[i]:indices[i + 1]]):
                            to_be_examined += line + "\n"
                            line = de_tok(line.split())
                            try:
                                words = line.split()
                                pre = words[words.index(de_head) - 1]
                                replace_pre = gender_change[pre]['m']
                                words[words.index(de_head) - 1] = replace_pre
                                line = ' '.join(words)
                            except ValueError:
                                words = tok(line)
                                pre = words[words.index(de_head) - 1]
                                replace_pre = gender_change[pre]['m']
                                words[words.index(de_head) - 1] = replace_pre
                                line = de_tok(words)
                            count_preword[pre] += 1
                            line = line.replace(de_head, gender_instance[0].capitalize())
                            try:
                                context, sent = line.split('<SEP>')
                            except ValueError:
                                context, sent = line.split('< SEP >')
                            if context:
                                context = ' '.join(tok(norm(context)))
                            sent = ' '.join(tok(norm(sent)))
                            line = context + (' <SEP> ' if context else '<SEP> ') + sent + '\n'
                            de_file.write(line)
                            modified = True
                            to_be_examined += line + '\n\n\n'
                        modified_indices.append(i)
                except KeyError:
                    pass
        if not modified:
            for j, line in enumerate(de_lines[indices[i]:indices[i + 1]]):
                de_file.write(line)
        modified = False
print(sorted(count_preword.items(), key=lambda x: x[1], reverse=True))

print('MODIFIED EXAMPLES:' + str(len(modified_indices)))
# command_de = f'subword-nmt apply-bpe -c ../ted_data/train/ende.bpe --glossaries "<SEP>" < ../ContraPro_Dario/ted/{modification_name}_de_tok.txt > tmp_de.txt'
# os.system(command_de)
#
# with open('tmp_de.txt', 'r') as tmp_de, open(f'../ContraPro_Dario/modified/{modification_name}_de_bpe.txt',
#                                              'w') as bpe_de:
#     for line in tmp_de:
#         bpe_de.write(line)
#
# os.system('rm -rf tmp_de.txt')
# shutil.copy('../ContraPro_Dario/en_tok.txt', f'../ContraPro_Dario/modified/{modification_name}_en_tok.txt')
# shutil.copy('../ContraPro_Dario/en_bpe.txt', f'../ContraPro_Dario/modified/{modification_name}_en_bpe.txt')
# pickle.dump(modified_indices, open('../ContraPro_Dario/modified/modified_indices.pkl', 'wb'))
