import glob
import re
from random import sample
import xml.etree.ElementTree as ET
import config


def get_gender_dict(dict_cc_file=config.resources_dir / 'dict_cc_original.txt', en_key=False):
    pattern = r'\[.*?\]|\(.*?\)'
    with open(dict_cc_file, 'r') as file:
        genders = dict()
        retrieved = 0
        for line in file:
            if line[0] != '#' and len(line) > 2:
                en, de = line.split(' :: ')
                de = re.sub(pattern, '', de)
                en = re.sub(pattern, '', en)
                if len(de.split()) == 2:
                    word, gender = de.split()
                    gender = gender.replace('{', '').replace('}', '').strip()
                    if gender in ['m', 'f', 'n']:
                        retrieved += 1
                        if en_key:
                            genders[en.lower().strip()] = (word.lower().strip(), gender)
                        else:
                            genders[word.lower()] = gender
                else:
                    pass
        return genders


def get_gender(mapping, word, head=None):
    result = mapping.get(word.lower())
    if result is None:
        result = mapping.get(head.lower())
    return result


def get_word2definite_article(lang):
    d = dict()
    with open(config.resources_dir / ('DET2definiteDET_' + lang), 'r') as file:
        for line in file:
            line = line.split()
            if len(line) == 1:
                d[line[0]] = ''
            else:
                d[line[0]] = line[1]
    return d


def get_sentence_idx(amount_samples=None):
    indices = [list(map(int, line.strip().split())) for line in open(
        config.adversarial_data_dir / 'sentence_groups.txt', 'r').readlines()]
    if amount_samples is None:
        return [idx_pair[0] for idx_pair in indices]
    else:
        return [idx_pair[0] for idx_pair in sample(indices, amount_samples)]

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
    for filepath in glob.glob(str(config.germanet_v120_xml_path / 'nomen*.xml')):
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

