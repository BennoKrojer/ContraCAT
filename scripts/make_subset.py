import pickle
import json

contrapro = json.load(open('../ContraPro/contrapro.json','r'))
contrapro_sub = []
indices = [int(line.strip()) for line in
           open('../ContraPro_Dario/sentence_groups.txt', 'r').readlines()]

f = open('../ContraPro_Dario/subtitle_bpe/modified/synonyms/female/female_de_tok.txt').readlines()
m = open('../ContraPro_Dario/subtitle_bpe/modified/synonyms/male/male_de_tok.txt').readlines()
n = open('../ContraPro_Dario/subtitle_bpe/modified/synonyms/neutral/neutral_de_tok.txt').readlines()
no_mod = open('../ContraPro_Dario/subtitle_bpe/contrapro.text.tok.prev.de.de').readlines()
modified_idx = []

for i, idx in enumerate(indices[:-1]):
    if f[idx] != no_mod[idx] or m[idx] != no_mod[idx] or n[idx] != no_mod[idx]:
        contrapro_sub.append(contrapro[i])
        modified_idx.append(i)

json.dump(contrapro_sub, open('../ContraPro/contrapro_synonym_subset.json', 'w'), indent=2)
pickle.dump(modified_idx, open('../ContraPro/synonym_subset.pkl', 'wb'))