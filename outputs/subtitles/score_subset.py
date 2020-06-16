import os
import pickle


indices = [int(line.strip()) for line in
           open('../../ContraPro_Dario/sentence_groups.txt', 'r').readlines()]

subset_indices = pickle.load(open('../../ContraPro/synonym_subset.pkl', 'rb'))
for file in os.listdir('normal/'):
    if "global" not in file:
        scores = open('normal/'+file).readlines()
        with open('normal/'+file+'_synonym_subset', 'w') as file:
            for i, idx in enumerate(indices[:-1]):
                if i in subset_indices:
                    start, end = indices[i], indices[i+1]
                    file.write(''.join(scores[start:end]))