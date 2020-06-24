import glob
import os
import pickle


indices = [int(line.strip()) for line in
           open('../../ContraPro_Dario/subtitle_bpe/sentence_groups.txt', 'r').readlines()]

subset_indices = pickle.load(open('../../ContraPro/synonym_subset.pkl', 'rb'))
for file in glob.glob('../../ContraPro_Dario/subtitle_bpe/modified/synonyms/*/*/scores'):
        scores = open(file).readlines()
        with open(file+'_subset', 'w') as sub_file:
            for i, idx in enumerate(indices[:-1]):
                if i in subset_indices:
                    start, end = indices[i], indices[i+1]
                    sub_file.write(''.join(scores[start:end]))