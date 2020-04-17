import difflib
import json
import pickle
import string
from collections import defaultdict

import numpy as np
from scripts.sample_modifications import get_sentence_idx


def get_groundtruth_translations():
    idx = get_sentence_idx()
    en = np.array(open('../ContraPro_Dario/contrapro.text.tok.prev.en.en', 'r').readlines())[idx[:-1]].tolist()
    de = np.array(open('../ContraPro_Dario/contrapro.text.tok.prev.de.de', 'r').readlines())[idx[:-1]].tolist()
    return list(zip(en, de)), idx


# def get_predicted_translations(scores, source, idx):
#

def align_pad(groundtruth, mistake_mod):
    if len(mistake_mod) - len(groundtruth) == 4:
        new_mistake = []
        i = 0
        while i < len(mistake_mod):
            if mistake_mod[i:i+3] == ['von', 'der', 'Katze']:
                i += 3
            if mistake_mod[i:i+2] == ['the', 'cat']:
                new_mistake.append('XXX')
                i += 2
            else:
                new_mistake.append(mistake_mod[i])
                i += 1
        return new_mistake
    else:
        return []


def load_dets(lang):
    d = dict()
    with open('DET2definiteDET_'+lang, 'r') as file:
        for line in file:
            line = line.split()
            if len(line) == 1:
                d[line[0]] = ''
            else:
                d[line[0]] = line[1]
    return d


def load_gender_change(filename):
    d = dict()
    with open(filename, 'r') as file:
        for line in file:
            line = line.split()
            if len(line) == 1:
                d[line[0]] = line[0]
            else:
                d[line[0]] = line[1]
    return d


def main(A, B, scoresA, sourceA_en, sourceA_de, scoresB, sourceB_en, sourceB_de, result_file, modified_idx, stats=False):
    groundtruth, idx = get_groundtruth_translations()
    # if scoresA == 'groundtruth':
    #     sentencesB =
    # else:
    result_file.write(f'A: {A}\n')
    result_file.write(f'B: {B}\n\n')
    both = []
    onlyAwrong = []
    onlyBwrong = []
    none = []
    shifts = defaultdict(int)
    for example_id, (start, end) in enumerate(list(zip(idx, idx[1:]))):
        if example_id in modified_idx:
            local_scoresA = list(map(lambda x: float(x.strip()), scoresA[start:end]))
            local_scoresB = list(map(lambda x: float(x.strip()), scoresB[start:end]))
            best_idA = np.argmin(local_scoresA)

            if scoresA == 'groundtruth':
                best_idA = 0
            best_idB = np.argmin(local_scoresB)
            wordsA = sourceA_de[start + best_idA].split()
            wordsB = sourceA_de[start + best_idB].split()
            diff = list(set([(b.lower(), a.lower()) for a, b in zip(wordsA, wordsB) if a != b]))
            if len(diff) > 0:
                shifts[diff[0]] += 1
            else:
                wordsA = sourceA_de[start + best_idA].split()
                wordsB = sourceA_de[start + (0 if best_idA == 1 else 1)].split()
                remained = [a.lower() for a, b in zip(wordsA, wordsB) if a.lower() != b.lower()][0]
                shifts[(remained, remained)] += 1
            if best_idA != 0 and best_idB != 0:
                both.append((groundtruth[example_id], '->\n'.join((sourceA_en[start+best_idA], sourceA_de[start+best_idA])), '\n->\n'.join((sourceB_en[start+best_idB], sourceB_de[start+best_idB]))))
            if best_idA != 0 and best_idB == 0:
                onlyAwrong.append((groundtruth[example_id], '->\n'.join((sourceA_en[start+best_idA], sourceA_de[start+best_idA]))))
            if best_idB != 0 and best_idA == 0:
                onlyBwrong.append((groundtruth[example_id], '->\n'.join((sourceB_en[start+best_idB], sourceB_de[start+best_idB]))))
            if best_idB == 0 and best_idA == 0:
                none.append((groundtruth[example_id], '->\n'.join((sourceA_en[start+best_idA], sourceA_de[start+best_idA])), '\n->\n'.join((sourceB_en[start+best_idB], sourceB_de[start+best_idB]))))
    print(shifts)
    #stats
    if stats:
        nr_modification_errors = len(onlyBwrong)
        count = defaultdict(int)
        german_modified_dets = load_dets("de").values()
        for item in onlyAwrong:
            groundtruth = "".join([char for char in (item[0][0] + item[0][1]) if char not in string.punctuation]).replace('aposs', '').split()
            mistake_mod = "".join([char for char in item[1] if char not in string.punctuation]).replace('\n->\n', '').replace('aposs', '').split()
            # new_mistake_mod = align_pad(groundtruth, mistake_mod) # has to be one for onlyA
            for _, (ground, mod) in enumerate(zip(groundtruth, mistake_mod)):
                # if ground == mod or "the man's" in mod:
                #     continue
                if ground != mod and mod != "XXX" and mod.lower().strip() not in german_modified_dets:
                    count[(ground.lower(), mod.lower())] += 1
                    if mod in ["er", "sie"]:
                        print("GROUNDTRUTH:" + " ".join(groundtruth))
                        print(f"SHIFT FROM {ground} to {mod}: {' '.join(mistake_mod)}\n")
                    break

        print("Statistics of errors (counts of how the gender shifted, e.g. er -> sie):\n")
        print("Total errors: " + str(nr_modification_errors) + "\n")
        for key, value in count.items():
            print(f'{key[1]} -> {key[0]}: {value}') # 0 -> 1 for onlyA

    else:
        result_file.write('both A & B wrong:\n\n')
        for item in both:
            result_file.write('GOLD:\n')
            result_file.write(f'{item[0][0]}->\n{item[0][1]}\n')
            result_file.write(f'{A} PREDICTED:\n')
            result_file.write(f'{item[1]}\n')
            result_file.write(f'{B} PREDICTED:\n')
            result_file.write(f'{item[2]}--------\n')

        result_file.write('none wrong:\n\n')

        for item in none:
            result_file.write('GOLD:\n')
            result_file.write(f'{item[0][0]}->\n{item[0][1]}\n')
            result_file.write(f'{A} PREDICTED:\n')
            result_file.write(f'{item[1]}\n')
            result_file.write(f'{B} PREDICTED:\n')
            result_file.write(f'{item[2]}--------\n')

        result_file.write(f'only {A} wrong:\n\n')

        for item in onlyAwrong:
            result_file.write('GOLD:\n')
            result_file.write(f'{item[0][0]}->\n{item[0][1]}\n')
            result_file.write(f'{A} PREDICTED:\n')
            result_file.write(f'{item[1]}--------\n')

        result_file.write(f'only {B} wrong:\n\n')

        for item in onlyBwrong:
            result_file.write('GOLD:\n')
            result_file.write(f'{item[0][0]}->\n{item[0][1]}\n')
            result_file.write(f'{B} PREDICTED:\n')
            result_file.write(f'{item[1]}--------\n')


if __name__ == '__main__':

    scoresA = open('../outputs/subtitles/synonyms/female/concat22', 'r')
    scoresB = open('../outputs/subtitles/normal/concat22', 'r')
    sourceA_en = open('../ContraPro_Dario/modified/synonyms/female/female_en_tok.txt', 'r')
    sourceA_de = open('../ContraPro_Dario/modified/synonyms/female/female_de_tok.txt', 'r')
    sourceB_en = open('../ContraPro_Dario/contrapro.text.tok.prev.en.en', 'r')
    sourceB_de = open('../ContraPro_Dario/contrapro.text.tok.prev.de.de', 'r')
    modified_idx = pickle.load(open('../ContraPro_Dario/modified/synonyms/female/modified_indices.pkl','rb'))
    results = open('../outputs/subtitles/compare/normal-female_synonym', 'w')
    A = 'female'
    B = 'normal'
    stats_mode = False
    main(A, B, scoresA.readlines(), sourceA_en.readlines(), sourceA_de.readlines(), scoresB.readlines(), sourceB_en.readlines(), sourceB_de.readlines(), results, modified_idx, stats=stats_mode)