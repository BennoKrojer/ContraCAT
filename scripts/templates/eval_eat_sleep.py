import json
import numpy

gender_order = ['m', 'f', 'n']
variant = 'animacy/'
predictions = {'correct': [], 'false': []}
correct = open(f'../../templates/animals/{variant}/correct', 'r').readlines()
scores = open(f'../../outputs/templates/animals/{variant}/concat22', 'r').readlines()
en = open(f'../../templates/animals/{variant}/en_tok', 'r').readlines()
de = open(f'../../templates/animals/{variant}/de_tok', 'r').readlines()

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
json.dump(predictions, open(f'../../outputs/templates/animals/{variant}/results.json', 'w'), indent=2)
