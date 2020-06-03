import spacy
import pandas as pd
from nltk.corpus import wordnet
from tqdm import tqdm

nlp_en = spacy.load("en_core_web_sm")

valid_pos_seqs = [['PRP$', 'NN'], ['DT', 'NN'], ['DT', 'JJ', 'NN'], ['DT', 'NN', 'NN'],
                  ['PRP$', 'JJ', 'NN']]

df = pd.read_csv('antecedent_aligments', sep='\t')

modified_antes = []
for i, row in tqdm(df.iterrows()):
    en_sentence = row['src_sent']
    ante = row['antecedent']
    if isinstance(ante, str):
        pos_tags = [i.tag_ for i in nlp_en(ante)]
        if pos_tags in valid_pos_seqs:
            ante_np = ante.split()[-1]
            synsets = wordnet.synsets(ante_np)
            if synsets:
                synonyms = synsets[0].lemmas()
                new_antes = []
                for synonym in synonyms:
                    modified = ante.split()[:-1] + [synonym.name()]
                    if '_' not in synonym.name():
                        new_antes.append(' '.join(modified))
                if len(new_antes) > 1:
                    new_antes_str = ','.join(new_antes)
                    modified_antes.append(new_antes_str)
                    continue
    modified_antes.append('')

df['modified_antecedent'] = modified_antes

df.to_csv('antecedents_alignments_modified', sep='\t', index=False)