import glob
import json
import os
import pickle
import re
from collections import defaultdict
import numpy as np
import spacy
import nltk
import tqdm
from mosestokenizer import MosesDetokenizer, MosesPunctuationNormalizer, MosesTokenizer
from nltk.corpus import wordnet

from scripts.compare_scores import load_dets, load_gender_change
from scripts.sample_modifications import get_sentence_idx
import xml.etree.ElementTree as ET

nltk.download('wordnet')
nlp_en = spacy.load("en_core_web_sm")
np.random.seed(42)
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


def get_genders():
    pattern = r'\[.*?\]|\(.*?\)'
    with open('dict_cc_original.txt', 'r') as file:
        genders = dict()
        retrieved = 0
        for line in file:
            if line[0] != '#' and len(line) > 2:
                _, de = line.split(' :: ')
                de = re.sub(pattern, '', de)
                if len(de.split()) == 2:
                    word, gender = de.split()
                    gender = gender.replace('{', '').replace('}', '').strip()
                    if gender in ['m', 'f', 'n']:
                        retrieved += 1
                        genders[word.lower().strip()] = gender
                else:
                    # print(de_full_text)
                    pass
        print("!!!!!!!!!!RETRIEVED:" + str(retrieved))
        return genders


results = []
de2gender = get_genders()
indices = get_sentence_idx()
nn_count = 0
modifiable_count = 0
different_gender_count = 0

modification_name = 'augm_synoynm'
folder = 'synonym_augmentation'
model = 'subtitles'

de_lines = open('../ContraPro_Dario/de_tok.txt', 'r').readlines()
en_lines = open('../ContraPro_Dario/en_tok.txt', 'r').readlines()
bpe_en_lines = open('../ContraPro_Dario/en_bpe.txt', 'r').readlines()
output_de = f'../ContraPro_Dario/{folder}/{model}/{modification_name}_de_tok.txt'
output_en = f'../ContraPro_Dario/{folder}/{model}/{modification_name}_en_tok.txt'
de_file_acc = []
en_file_acc = []
split = False

det2def_det = load_dets('de_full_text')
gender_change = {'m': load_gender_change('2male_de'), 'f': load_gender_change('2female_de'), 'n': load_gender_change(
    '2neutral_de')}
contrapro = json.load(open('../ContraPro/contrapro.json', 'r'))
idx = get_sentence_idx()
new_contrapro = []

modified = False
cached = os.path.exists(f'../ContraPro_Dario/synonym_augmentation/{model}/modified_indices.pkl')
modified_indices_lines = []
if cached:
    modified_indices = pickle.load(open(f'../ContraPro_Dario/synonym_augmentation/{model}/modified_indices.pkl', 'rb'))
else:
    modified_indices = []
modified_idx_de = set()
modified_de = defaultdict(list)
count_preword = defaultdict(int)


def get_gender2sent(example):
    order = []
    map = {'er' : 'm', 'sie':'f','es':'n', 'Fem':'f', 'Neut':'n', 'Masc':'m'}
    correct_gender = map[example['ref pronoun'].lower()]
    order.append(correct_gender)
    # res[correct_gender] = example['ref segment']
    for contrastive in example['errors']:
        order.append(map[contrastive['replacement deprecated_gender']])
        # res[map[contrastive['replacement deprecated_gender']]] = contrastive['contrastive']
    unusual = len(example['errors']) > 2
    return order, unusual


with MosesPunctuationNormalizer('de_full_text') as norm, MosesTokenizer('de_full_text') as tok, MosesDetokenizer('de_full_text') as de_tok,\
        open(output_de, 'w') as de_file, open(output_en, 'w') as en_file:
    for i in tqdm.tqdm(modified_indices if cached else range(len(contrapro))):
        modified = False
        example = contrapro[i]
        gender_order, unusual = get_gender2sent(example)
        head = example['src ante head lemma']
        tag = example["src ante head pos"]
        de_head = example['ref ante head lemma']
        dist = example['ante distance']
        en_context = clean_context(en_lines[indices[i]])
        de_context = clean_context(de_lines[indices[i]])
        if 'NN' in tag and de_head is not None and dist < 2 and (de_head in tok(de_context) or de_head  in de_context.split()):
            nn_count += 1
            synset = disambiguate(head, en_context, wordnet.synsets(head))  # if it is not ".n" you can ignore it
            if synset:
                id = synset._offset
                try:
                    lemma_id = en2lex_id[id]
                    german_synset = lexid2synset[lemma_id]
                    original_gender = de2gender[de_head.lower()]
                    german_synonyms = {de_head: original_gender}
                    for word, compound_head in german_synset:
                        try:
                            if compound_head:
                                gender = de2gender[compound_head.lower()]
                            else:
                                gender = de2gender[word.lower()]
                            german_synonyms[word] = gender
                        except KeyError:
                            continue
                    if len(german_synonyms) > 1:
                        de_sentences = []
                        en_sentences = []
                        for synonym, gender in german_synonyms.items():
                            line = de_lines[indices[i]+gender_order.index(gender)]
                            line = de_tok(line.split())
                            if original_gender != gender:
                                try:
                                    words = line.split()
                                    pre = words[words.index(de_head) - 1]
                                    replace_pre = gender_change[gender][pre]
                                    words[words.index(de_head) - 1] = replace_pre
                                    line = ' '.join(words)
                                except ValueError:
                                    words = tok(line)
                                    pre = words[words.index(de_head) - 1]
                                    replace_pre = gender_change[gender][pre]
                                    words[words.index(de_head) - 1] = replace_pre
                                    line = de_tok(words)
                            line = line.replace(de_head, synonym.capitalize())
                            try:
                                context, sent = line.split('<SEP>')
                            except ValueError:
                                context, sent = line.split('< SEP >')
                            if context:
                                context = ' '.join(tok(norm(context)))
                            sent = ' '.join(tok(norm(sent)))
                            line = context + (' <SEP> ' if context else '<SEP> ') + sent + '\n'
                            if not split:
                                de_file.write(line)
                                en_file.write(en_lines[indices[i]+gender_order.index(gender)])
                                modified = True
                            else:
                                de_sentences.append(line)
                                en_sentences.append(en_lines[indices[i] + gender_order.index(gender)])
                        # if not cached:
                        # modified_indices.append(i)
                        for ind in range(indices[i], indices[i+1]):
                            modified_indices_lines.append(ind)
                        if de_sentences and np.random.randint(2) == 1:
                            modified = True
                            de_file.write(''.join(de_sentences))
                            en_file.write(''.join(en_sentences))
                except KeyError:
                    pass
        if not modified:
            new_contrapro.append(example)


bpe = '../ted_data/train/ende.bpe' if model == 'ted' else '../models_dario/subtitles/ende.bpe'
command_de = f'subword-nmt apply-bpe -c {bpe} --glossaries "<SEP>" < {output_de} > {output_de.replace("tok", "bpe")}'
command_en = f'subword-nmt apply-bpe -c {bpe} --glossaries "<SEP>" < {output_en} > {output_en.replace("tok", "bpe")}'
os.system(command_de)
os.system(command_en)

pickle.dump(modified_indices, open(f'../ContraPro_Dario/{folder}/{model}/modified_indices_examples.pkl', 'wb'))
pickle.dump(modified_indices_lines, open(f'../ContraPro_Dario/{folder}/{model}/modified_indices_lines.pkl', 'wb'))
# json.dump(new_contrapro, open(f'../ContraPro/contrapro_no_augm{"_half" if split else ""}.json', 'w'), indent=2)
