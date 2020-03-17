import argparse
import sys

import numpy as np
from scripts.sample_modifications import get_sentence_idx


def get_groundtruth_translations():
    idx = get_sentence_idx()
    en = np.array(open('../ContraPro_Dario/contrapro.text.tok.prev.en.en', 'r').readlines())[idx[:-1]].tolist()
    de = np.array(open('../ContraPro_Dario/contrapro.text.tok.prev.de.de', 'r').readlines())[idx[:-1]].tolist()
    return list(zip(en, de)), idx


# def get_predicted_translations(scores, source, idx):
#

def main(A, B, scoresA, sourceA_en, sourceA_de, scoresB, sourceB_en, sourceB_de, result_file):
    groundtruth, idx = get_groundtruth_translations()
    # if scoresA == 'groundtruth':
    #     sentencesB =
    # else:
    result_file.write(f'A: {A}\n')
    result_file.write(f'B: {B}\n\n')
    both = []
    onlyAwrong = []
    onlyBwrong = []
    for example_id, (start, end) in enumerate(list(zip(idx, idx[1:]))):
        local_scoresA = list(map(lambda x: float(x.strip()), scoresA[start:end]))
        local_scoresB = list(map(lambda x: float(x.strip()), scoresB[start:end]))
        best_idA = np.argmin(local_scoresA)
        if scoresA == 'groundtruth':
            best_idA = 0
        best_idB = np.argmin(local_scoresB)
        if best_idA != 0 and best_idB != 0:
            both.append((groundtruth[example_id], '->\n'.join((sourceA_en[start+best_idA], sourceA_de[start+best_idA])), '\n->\n'.join((sourceB_en[start+best_idB], sourceB_de[start+best_idB]))))
        if best_idA != 0 and best_idB == 0:
            onlyAwrong.append((groundtruth[example_id], '->\n'.join((sourceA_en[start+best_idA], sourceA_de[start+best_idA]))))
        if best_idB != 0 and best_idA == 0:
            onlyBwrong.append((groundtruth[example_id], '->\n'.join((sourceB_en[start+best_idB], sourceB_de[start+best_idB]))))

    result_file.write('both A & B wrong:\n\n')
    for item in both:
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


if __name__=='__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--scoresA', type=argparse.FileType('r'),
    #                     default='groundtruth', metavar='PATH',
    #                     help="File with scores (one per line). If nothing passed, using groundtruth")
    # parser.add_argument('--sourceA', type=argparse.FileType('r'),
    #                     default='groundtruth', metavar='PATH',
    #                     help="File with (modified) source")
    # parser.add_argument('--scoresB', type=argparse.FileType('r'),
    #                     default=sys.stdin, metavar='PATH',
    #                     help="File with scores (one per line)")
    # parser.add_argument('--sourceB', type=argparse.FileType('r'),
    #                     default='groundtruth', metavar='PATH',
    #                     help="File with (modified) source")
    # parser.add_argument('--results', type=argparse.FileType('w'),
    #                     default=sys.stdout, metavar='PATH',
    #                     help="Filepath to write results")

    # = parser.parse_)
    scoresA = open('../outputs/normal/output-concat22', 'r')
    scoresB = open('../outputs/he_said/concat22_quotes', 'r')
    sourceA_en = open('../ContraPro_Dario/contrapro.text.tok.prev.en.en', 'r')
    sourceA_de = open('../ContraPro_Dario/contrapro.text.tok.prev.de.de', 'r')
    sourceB_en = open('../ContraPro_Dario/modified/he_said/he_said_en_tok.txt', 'r')
    sourceB_de = open('../ContraPro_Dario/modified/he_said/er_sagte_de_tok.txt', 'r')
    results = open('../outputs/compare/normal-he_said', 'w')
    A = 'normal'
    B = 'he_said'
    main(A,B, scoresA.readlines(), sourceA_en.readlines(), sourceA_de.readlines(), scoresB.readlines(), sourceB_en.readlines(), sourceB_de.readlines(), results)