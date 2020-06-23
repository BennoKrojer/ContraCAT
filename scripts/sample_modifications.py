import glob
from random import sample
import os
import numpy as np


def get_sentence_idx(amount_samples=None):
    indices = [list(map(int, line.strip().split())) for line in open('../ContraPro_Dario/sentence_groups.txt', 'r').readlines()]
    if amount_samples is None:
        return [idx_pair[0] for idx_pair in indices]
    else:
        return [idx_pair[0] for idx_pair in sample(indices, amount_samples)]


if __name__=='__main__':
    sample_idx = get_sentence_idx(amount_samples=200)
    source = '../ContraPro_Dario/ted'
    mod_dirs = os.listdir(source)
    all_samples = []
    for mod_dir in mod_dirs:
        for file in glob.glob(os.path.join(source, mod_dir, '*en_tok*')):
            lines = np.array(open(file, 'r').readlines())
            sampled_lines = lines[sample_idx]
            all_samples.append(sampled_lines.tolist())

    with open('../ContraPro_Dario/modified/evaluate_modifications.txt', 'w') as file:
        for line in list(zip(*all_samples)):
            for mod_line in line:
                file.write('\t'.join(mod_line.split('<SEP>')))
