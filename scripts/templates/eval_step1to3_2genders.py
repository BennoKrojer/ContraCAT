import json
from collections import defaultdict

import numpy
import os


def get_used_genders(sent):
    prev = sent.split('<SEP>')[0].lower()
    used_genders = []
    if "subject" in path:
        if "hat den" in prev:
            used_genders.append('m')
        if "hat die" in prev:
            used_genders.append('f')
        if "hat das" in prev:
            used_genders.append('n')
    else:
        if prev[:3] == 'der' or 'und der' in prev:
            used_genders.append('m')
        if prev[:3] == 'die' or 'und die' in prev:
            used_genders.append('f')
        if prev[:3] == 'das' or 'und das' in prev:
            used_genders.append('n')
    return used_genders


gender_order = ['m', 'f', 'n']
dir = '../../templates/final/2_coreference_step/overlap'
for model in ['standard', 'tuned', 'tuned_lowest']:
    for path, _, files in os.walk(dir):
        if 'correct' in files:
            predictions = {'correct': [], 'false': [], 'not_from_ants': []}
            words_correct = defaultdict(int)
            words_incorrect = defaultdict(int)
            distr_correct = {'m': 0, 'f': 0, 'n': 0}
            distr_incorrect = {'m': 0, 'f': 0, 'n': 0}
            correct = open(f'{path}/correct', 'r').readlines()
            scores = open(f'{path}/scores_{model}', 'r').readlines()
            en = open(f'{path}/en_tok', 'r').readlines()
            de = open(f'{path}/de_tok', 'r').readlines()

            chose_from_2ants = 0
            total = 0
            for i in range(0, len(scores) - 2, 3):
                g1, g2 = get_used_genders(de[i])
                id_g1, id_g2 = gender_order.index(g1), gender_order.index(g2)
                correct_gender = correct[i].split()[0]
                # pred = numpy.argmin(scores[i:i + 3])
                pred = id_g1 if float(scores[i + id_g1]) < float(scores[i + id_g2]) else id_g2
                pred_gender = gender_order[pred]

                if pred_gender in [g1, g2]:
                    chose_from_2ants += 1
                else:
                    predictions['not_from_ants'].append(de[i + pred])

                total += 1
                if correct_gender == pred_gender:
                    predictions['correct'].append(de[i + pred])
                    distr_correct[pred_gender] += 1
                    for word in de[i + pred].split(' '):
                        words_correct[word] += 1
                else:
                    predictions['false'].append(de[i + pred])
                    distr_incorrect[pred_gender] += 1
                    for word in de[i + pred].split(' '):
                        words_incorrect[word] += 1
            print(path)
            with open(f'{path}/2gender_result_{model}', 'w') as file:
                for key, val in predictions.items():
                    file.write(f'{key}: {len(val)}' + '\n')
                file.write(f'acc: {len(predictions["correct"])/total}\n')
                file.write(str(distr_correct) + '\n')
                file.write(str(distr_incorrect) + '\n')
                file.write(f'Chose gender from one of the ants: {str(chose_from_2ants)} / {str(total)} -> '
                           f'{str(chose_from_2ants / total)}\n')
                file.write(str(sorted(list(words_correct.items())[10:], key=lambda x: x[1], reverse=True)) + '\n')
                file.write(str(sorted(list(words_incorrect.items())[10:], key=lambda x: x[1], reverse=True)) + '\n')
            json.dump(predictions, open(f'{path}/2gender_result_{model}.json', 'w'), indent=2)
