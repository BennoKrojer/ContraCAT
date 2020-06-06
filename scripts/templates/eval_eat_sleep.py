import json
import numpy
import os

gender_order = ['m', 'f', 'n']
dir = '../../templates_SEP_fixed/gender'
for path, _, files in os.walk(dir):
    if len(files) == 7:
        predictions = {'correct': [], 'false': []}
        distr_correct = {'m':0, 'f':0, 'n':0}
        distr_incorrect = {'m':0, 'f':0, 'n':0}
        correct = open(f'{path}/correct', 'r').readlines()
        scores = open(f'{path}/concat22', 'r').readlines()
        en = open(f'{path}/en_tok', 'r').readlines()
        de = open(f'{path}/de_tok', 'r').readlines()

        for i in range(0, len(scores)-2, 3):
            correct_gender = correct[i].split()[0]
            pred = numpy.argmin(scores[i:i+3])
            pred_gender = gender_order[pred]

            if correct_gender == pred_gender:
                predictions['correct'].append(de[i+pred])
                distr_correct[pred_gender] += 1
            else:
                predictions['false'].append(de[i+pred])
                distr_incorrect[pred_gender] += 1
        print(path)
        for key, val in predictions.items():
            print(f'{key}: {len(val)}')
        print(distr_correct)
        print(distr_incorrect)
        print('\n')
        json.dump(predictions, open(f'{path}/results.json', 'w'), indent=2)
