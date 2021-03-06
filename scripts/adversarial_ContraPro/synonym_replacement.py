import json
import os
import nltk
import spacy
import tqdm
from mosestokenizer import MosesDetokenizer, MosesTokenizer
from nltk.corpus import wordnet
from scripts.adversarial_ContraPro.utils import get_gender_dict, get_sentence_idx, load_germanet, load_interlingual
import config


def write_modify():
    nlp_de = spacy.load("de_core_news_sm")
    gender_declination = json.load(open(config.resources_dir / 'german_declination.json'))
    en2lex_id = load_interlingual()
    lexid2synset = load_germanet()
    nltk.download('wordnet')
    de2gender = get_gender_dict(config.resources_dir / 'dict_cc_original.txt', en_key=False)
    indices = get_sentence_idx()
    contrapro = json.load(open(config.contrapro_file, 'r'))

    def get_new_prev(prev, gender, sentence, idx):
        upper = prev[0].isupper()
        old_prev = prev
        prev = prev.lower()
        article = gender_declination['article'].get(prev)
        if list(article.keys())[0] in ['m', 'f', 'n']:
            return article[gender].capitalize() if upper else article[gender]
        else:
            token = [t for t in nlp_de(sentence) if t.text == old_prev][idx]
            dep = token.dep_ if type == 'pronoun' else token.head.dep_
            if dep in ['sb', 'sp']:
                case = 'nom'
            elif dep[:2] == 'oa':
                case = 'acc'
            elif dep in ['da', 'op']:
                case = 'dat'
            elif dep in ['og', 'ag']:
                case = 'gen'
            else:
                case = 'nom'

            return article[case][gender].capitalize() if upper else article[case][gender]

    def get_synset_for_en_word(word):
        """
        given an English word, returns a synset of an other language.
        Requires a mapping from English synset to other-language synset, e.g. for German this is offered by GermaNet,
        which is not publicly available unfortunately.
        More information: https://uni-tuebingen.de/en/faculties/faculty-of-humanities/departments/modern-languages/department-of-linguistics/chairs/general-and-computational-linguistics/ressources/lexica/germanet/
        """
        synset = wordnet.synsets(word)[0]  # disambiguate by taking most frequent wordnet snyset
        id = synset._offset
        lemma_id = en2lex_id[id]
        german_synset = lexid2synset[lemma_id]
        return german_synset

    def get_different_gender_synonym(german_synset):
        for word, compound_head in german_synset:
            try:
                if compound_head:
                    new_gender = de2gender[compound_head.lower()]
                else:
                    new_gender = de2gender[word.lower()]
                if new_gender != original_gender and word.lower() != de_head.lower():
                    return word, new_gender
            except KeyError:
                continue
        return None, None

    de_lines = open(config.adversarial_data_dir / 'de.txt', 'r').readlines()
    en_lines = open(config.adversarial_data_dir / 'en.txt', 'r').readlines()
    output = config.adversarial_data_dir / 'synonyms'
    os.makedirs(output, exist_ok=True)
    modified_indices = []
    modified_contrapro_subset = []
    contrapro_subset = []
    idxxx = []
    gendermap = {'Fem': 'f', 'Masc': 'm', 'Neut': 'n'}

    with open(output / 'de.txt', 'w') as de_file, open(output / 'en.txt', 'w') as en_file, \
            MosesTokenizer('de') as tok, MosesDetokenizer('de') as detok:
        for i, example in tqdm.tqdm(enumerate(contrapro)):
            head = example['src ante head lemma']
            tag = example["src ante head pos"]
            de_head = example['ref ante head lemma']
            dist = example['ante distance']
            de_phrase = de_lines[indices[i]]

            gender_order = [gendermap[error['replacement gender']] for error in example['errors']]

            if 'NN' in tag and de_head and dist < 2 and de_head in tok(de_phrase) and wordnet.synsets(head):
                try:
                    original_gender = gendermap[example['ref ante head gender']]
                    german_synset = get_synset_for_en_word(head)
                    new_ante, new_gender = get_different_gender_synonym(german_synset)

                    if new_ante:
                        de_variations = []
                        for j, line in enumerate(de_lines[indices[i]:indices[i + 1]]):
                            words = tok(line)
                            pre = words[words.index(de_head) - 1]
                            pre_idx = -1
                            for w in words:
                                if w == pre:
                                    pre_idx += 1
                            replace_pre = get_new_prev(pre, new_gender, line, pre_idx)
                            words[words.index(de_head) - 1] = replace_pre
                            words[words.index(de_head)] = new_ante.capitalize()
                            line = detok(words)
                            context, sent = line.split('< SEP >')
                            line = context + '<SEP>' + sent + '\n'
                            de_variations.append(line)
                        best = de_variations[gender_order.index(new_gender) + 1]
                        de_variations[gender_order.index(new_gender) + 1] = de_variations[0]
                        de_variations[0] = best
                        for line in de_variations:
                            de_file.write(line)
                        for line in en_lines[indices[i]:indices[i + 1]]:
                            en_file.write(line)
                        modified_indices.append(i)

                        new_example = example.copy()
                        old_ref_pronoun = example['ref pronoun']
                        old_ref_segment = example['ref segment']
                        for error in new_example['errors']:
                            if new_gender == gendermap[error['replacement gender']]:
                                new_example['ref pronoun'] = error['replacement']
                                new_example['ref segment'] = error['contrastive']
                                new_example['ref ante head gender'] = new_gender
                                error['replacement gender'] = original_gender
                                error['contrastive'] = old_ref_segment
                                error['replacement'] = old_ref_pronoun
                        modified_contrapro_subset.append(new_example)
                        contrapro_subset.append(example)
                        idxxx.append(i)
                except (KeyError, AttributeError, ValueError) as e:
                    pass
    with open('../../modified_syn_idx', 'w') as f:
        for i in idxxx:
            f.write(str(i)+'\n')
    json.dump(modified_contrapro_subset, open(output / 'modified_contrapro_subset.json', 'w'), indent=2)
    json.dump(contrapro_subset, open(output / 'contrapro_subset.json', 'w'), indent=2)
    print('MODIFIED EXAMPLES:' + str(len(modified_indices)))


if __name__ == '__main__':
    write_modify()
