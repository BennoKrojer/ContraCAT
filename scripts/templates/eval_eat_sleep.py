import json
from collections import defaultdict

import numpy
import os

gender_order = ['m', 'f', 'n']
dir = '../../templates/final/baseline_sentence_level'
for model in ['baseline']:
    for path, _, files in os.walk(dir):
        if 'correct' in files:
            predictions = {'correct': [], 'false': []}
            words_correct = defaultdict(int)
            words_incorrect = defaultdict(int)
            distr_correct = {'m':0, 'f':0, 'n':0}
            distr_incorrect = {'m':0, 'f':0, 'n':0}
            correct = open(f'{path}/correct', 'r').readlines()
            scores = open(f'{path}/scores_{model}', 'r').readlines()
            en = open(f'{path}/en_tok', 'r').readlines()
            de = open(f'{path}/de_tok', 'r').readlines()

            for i in range(0, len(scores)-2, 3):
                correct_gender = correct[i].split()[0]
                pred = numpy.argmin(scores[i:i+3])
                pred_gender = gender_order[pred]

                if correct_gender == pred_gender:
                    predictions['correct'].append(de[i+pred])
                    distr_correct[pred_gender] += 1
                    for word in de[i+pred].split(' '):
                        words_correct[word] += 1
                else:
                    predictions['false'].append(de[i+pred])
                    distr_incorrect[pred_gender] += 1
                    for word in de[i+pred].split(' '):
                        words_incorrect[word] += 1
            print(path)
            with open(f'{path}/result_{model}', 'w') as file:
                for key, val in predictions.items():
                    file.write(f'{key}: {len(val)}'+'\n')
                file.write(str(distr_correct)+'\n')
                file.write(str(distr_incorrect)+'\n')
                file.write(str(sorted(list(words_correct.items())[10:], key=lambda x: x[1], reverse=True))+'\n')
                file.write(str(sorted(list(words_incorrect.items())[10:], key=lambda x: x[1], reverse=True))+'\n')
            json.dump(predictions, open(f'{path}/result_{model}.json', 'w'), indent=2)
