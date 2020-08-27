import glob
import os
import pickle


indices = [int(line.strip()) for line in
           open('../../data/adversarial_ContraPro/sentence_groups.txt', 'r').readlines()]

subset_indices = [int(i) for i in open('../../modified_poss_idx_best_friend', 'r').readlines()]
for file in glob.glob('../../outputs/subtitles/nested/noun_phrases/concat22_best_friend'):
        scores = open(file).readlines()
        with open(file+'_poss_subset_UpdatedInAug', 'w') as sub_file:
            for i, idx in enumerate(indices[:-1]):
                if i in subset_indices:
                    start, end = indices[i], indices[i+1]
                    sub_file.write(''.join(scores[start:end]))