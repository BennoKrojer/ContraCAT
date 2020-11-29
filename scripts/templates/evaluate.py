import argparse
import json
from argparse import ArgumentParser
from pathlib import Path

import numpy as np

GENDER_ORDER = ['m', 'f', 'n']


def order_eval(scores, correct, de, score_type='small'):
    counts = {'m': 0, 'f': 0, 'n': 0}
    result = {'first_pos': (counts.copy(), []),
              'second_pos': (counts.copy(), []),
              'same_antecedent': (counts.copy(), []),
              'other': (counts.copy(), [])}
    for i in range(0, len(scores) - 5, 6):
        local_scores = scores[i:i + 6]
        first_gender = correct[i][0]
        second_gender = correct[i + 5][0]
        bestidx1 = np.argmin(local_scores[:3]) if score_type == 'small' else np.argmax(local_scores[:3])
        bestidx2 = np.argmin(local_scores[3:]) if score_type == 'small' else np.argmax(local_scores[3:])

        if bestidx1 == bestidx2 and (GENDER_ORDER[bestidx2] == second_gender or GENDER_ORDER[bestidx2] == first_gender):
            key = 'same_antecedent'
        elif bestidx1 == GENDER_ORDER.index(first_gender) and bestidx2 == GENDER_ORDER.index(second_gender):
            key = 'first_pos'
        elif bestidx1 == GENDER_ORDER.index(second_gender) and bestidx2 == GENDER_ORDER.index(first_gender):
            key = 'second_pos'
        else:
            key = 'other'

        result[key][1].append(de[i + bestidx1].strip() + '///' + de[i + 3 + bestidx2].strip())
        result[key][0][first_gender] += 1
        result[key][0][second_gender] += 1

    return result


def standard_eval(scores, correct, de, score_type='small'):
    result = {'correct': ({'m': 0, 'f': 0, 'n': 0}, []), 'false': ({'m': 0, 'f': 0, 'n': 0}, [])}

    for i in range(0, len(scores) - 2, 3):
        correct_gender = correct[i].strip()
        local_scores = scores[i:i + 3]
        pred = np.argmin(local_scores) if score_type == 'small' else np.argmax(local_scores)
        pred_gender = GENDER_ORDER[pred]

        key = 'correct' if correct_gender == pred_gender else 'false'
        result[key][1].append(de[i + pred])
        result[key][0][pred_gender] += 1

    return result


def gender_eval(scores, de, score_type):
    result = ({'m': [0, []], 'f': [0, []], 'n': [0, []]})

    for i in range(0, len(scores) - 2, 3):
        local_scores = scores[i:i + 3]
        pred = np.argmin(local_scores) if score_type == 'small' else np.argmax(local_scores)
        pred_gender = GENDER_ORDER[pred]

        result[pred_gender][1].append(de[i + pred])
        result[pred_gender][0] += 1

    return result


def role_eval(scores, correct, de, score_type):
    result = {'subj': ({'m': 0, 'f': 0, 'n': 0}, []),
              'obj': ({'m': 0, 'f': 0, 'n': 0}, []),
              'other': ({'m': 0, 'f': 0, 'n': 0}, [])}

    for i in range(0, len(scores) - 2, 3):
        first_gender = correct[i].strip()[0]
        second_gender = correct[i].strip()[1]
        local_scores = scores[i:i + 3]
        pred = np.argmin(local_scores) if score_type == 'small' else np.argmax(local_scores)
        pred_gender = GENDER_ORDER[pred]
        if pred_gender == first_gender:
            key = 'subj'
        elif pred_gender == second_gender:
            key = 'obj'
        else:
            key = 'other'
        result[key][1].append(de[i + pred])
        result[key][0][pred_gender] += 1

    return result


def evaluate(args):
    scores = [line for line in args.scores.readlines() if line != '\n']
    correct = [line for line in open(Path(args.data_dir) / 'genders.txt', 'r').readlines() if line != '\n']
    de = [line for line in open(Path(args.data_dir) / 'de.txt', 'r').readlines() if line != '\n']
    if args.mode == 'standard':
        assert len(correct) == len(scores) == len(de)
        result = standard_eval(scores, correct, de, args.score_type)
    elif args.mode == 'order':
        assert len(correct) == len(scores) == len(de)
        result = order_eval(scores, correct, de, args.score_type)
    elif args.mode == 'grammatical_role':
        assert len(correct) == len(scores) == len(de)
        result = role_eval(scores, correct, de, args.score_type)
    elif args.mode == 'gender':
        assert len(scores) == len(de)
        result = gender_eval(scores, de, args.score_type)
    else:
        raise ValueError(f'{args.mode} is not a valid mode!')

    for key, (distr, _) in result.items():
        nested = isinstance(distr, dict)
        print(f'{key}: {sum(distr.values()) if nested else distr}')
        if nested:
            for key, val in distr.items():
                print(f'{key}: {val}')
        print('\n')
    if args.write_details:
        json.dump(result, open(Path(args.data_dir) / 'predictions.json', 'w'), indent=2)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--data_dir', required=True, help='Folder that contains de, en and gender-groundtruth files')
    parser.add_argument('--scores', type=argparse.FileType('r'), help='File that contains the scores. 1 score per '
                                                                      'line.')
    parser.add_argument('--score_type', default='small', help='Whether small or big score is a good score, '
                                                              'default is small')
    parser.add_argument('--mode', default='standard',
                        help='Default is standard, when there is a groundtruth translation for it possible. For prior '
                             'experiments, there are different modes, as there is no groundtruth: order, '
                             'grammatical role & gender')
    parser.add_argument('--write_details', action='store_true',
                        help='Whether to write correct and incorrect predictions into json file in data_dir')
    args = parser.parse_args()
    evaluate(args)