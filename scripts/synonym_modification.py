import glob
import json
import os
import pickle
import re
import shutil
from collections import defaultdict
import nltk
import tqdm
from mosestokenizer import MosesDetokenizer, MosesPunctuationNormalizer, MosesTokenizer
from nltk.corpus import wordnet

from scripts.compare_scores import load_dets, load_gender_change
from scripts.sample_modifications import get_sentence_idx
import xml.etree.ElementTree as ET
from scripts.utils import get_genders

nltk.download('wordnet')
# nlp_en = spacy.load("en_core_web_sm")

def load_interlingual():
    root = ET.parse('../GermaNet/GN_V120/GN_V120_XML/interLingualIndex_DE-EN.xml').getroot()
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
    for filepath in glob.glob('../GermaNet/GN_V120/GN_V120_XML/nomen*.xml'):
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
    context = MosesDetokenizer('en_full_text')(context.split())
    return context


def disambiguate(word, context, synsets):
    if synsets:
        return synsets[0]
    else:
        return None


results = []
de2gender = get_genders()
indices = get_sentence_idx()
en_context_lines = open('../ContraPro_Dario/contrapro.text.tok.prev.en.en', 'r').readlines()
de_context_lines = open('../ContraPro_Dario/contrapro.text.tok.prev.de.de', 'r').readlines()
nn_count = 0
modifiable_count = 0
different_gender_count = 0
modifications_file = open('possible_modifications', 'w')

modification_name = 'male'
de_lines = open('../ContraPro_Dario/contrapro.text.tok.prev.de.de', 'r').readlines()
en_lines = open('../ContraPro_Dario/contrapro.text.tok.prev.en.en', 'r').readlines()
output_de = f'../ContraPro_Dario/modified/{modification_name}_de_tok.txt'
output_en = f'../ContraPro_Dario/modified/{modification_name}_en_tok.txt'

det2def_det = load_dets('de_full_text')
gender_change = load_gender_change('2male_de')
contrapro = json.load(open('../ContraPro/contrapro.json', 'r'))
idx = get_sentence_idx()

modified = False
modified_indices = []
modified_idx_de = set()
modified_de = defaultdict(list)
to_be_examined = ""
count_preword = defaultdict(int)
with MosesPunctuationNormalizer('de_full_text') as norm, MosesTokenizer('de_full_text') as tok, MosesDetokenizer('de_full_text') as de_tok,\
        open(output_de, 'w') as de_file:
    for i, example in tqdm.tqdm(enumerate(contrapro)):
        head = example['src ante head lemma']
        tag = example["src ante head pos"]
        de_head = example['ref ante head lemma']
        dist = example['ante distance']
        en_context = clean_context(en_context_lines[indices[i]])
        de_context = clean_context(de_context_lines[indices[i]])
        if 'NN' in tag and de_head is not None and dist < 2 and (de_head in tok(de_context) or de_head in de_context.split()):
            nn_count += 1
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
                        for j, line in enumerate(de_lines[indices[i]:indices[i+1]]):
                            to_be_examined += line + "\n"
                            line = de_tok(line.split())
                            try:
                                words = line.split()
                                pre = words[words.index(de_head) - 1]
                                replace_pre = gender_change[pre]
                                words[words.index(de_head) - 1] = replace_pre
                                line = ' '.join(words)
                            except ValueError:
                                words = tok(line)
                                pre = words[words.index(de_head) - 1]
                                replace_pre = gender_change[pre]
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
command_de = f'subword-nmt apply-bpe -c ../ted_data/train/ende.bpe --glossaries "<SEP>" < ../ContraPro_Dario/modified/{modification_name}_de_tok.txt > tmp_de.txt'
os.system(command_de)

with open('tmp_de.txt', 'r') as tmp_de, open(f'../ContraPro_Dario/modified/{modification_name}_de_bpe.txt', 'w') as bpe_de:
    for line in tmp_de:
        bpe_de.write(line)

os.system('rm -rf tmp_de.txt')
shutil.copy('../ContraPro_Dario/contrapro.text.tok.prev.en.en', f'../ContraPro_Dario/modified/{modification_name}_en_tok.txt')
shutil.copy('../ContraPro_Dario/contrapro.text.bpe.prev.en.en', f'../ContraPro_Dario/modified/{modification_name}_en_bpe.txt')
pickle.dump(modified_indices, open('../ContraPro_Dario/modified/modified_indices.pkl', 'wb'))
