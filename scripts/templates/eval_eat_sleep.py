import json
import numpy

gender_order = ['m','f','n']
predictions = {'correct': [], 'false': []}
correct = open('../../templates/animals/correct', 'r').readlines()
scores = open('../../outputs/templates/concat22_pattern_match', 'r').readlines()
en = open('../../templates/animals/en_tok', 'r').readlines()
de = open('../../templates/animals/de_tok', 'r').readlines()

for i in range(0, len(scores)-2, 3):
    correct_gender = correct[i].split()[0]
    pred = numpy.argmin(scores[i:i+3])
    pred_gender = gender_order[pred]

    if correct_gender == pred_gender:
        predictions['correct'].append(de[i+pred])
    else:
        predictions['false'].append(de[i+pred])


for key, val in predictions.items():
    print(f'{key}: {len(val)}')
json.dump(predictions, open('../../outputs/templates/eat_sleep_results.json', 'w'), indent=2)