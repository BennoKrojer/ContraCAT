import json
from pathlib import Path

best = float('inf')
genders = ['er', 'sie', 'es']
predictions = {'er': [], 'sie': [], 'es': []}
best_en = ''
best_de = ''
model = "tuned_lowest"
dir = '../../templates/final/0_priors/verb/'
for i, (score, de, en) in enumerate(zip(open(f'{dir}scores_{model}', 'r'),
                                        open(f'{dir}de_tok', 'r').readlines(),
                                        open(f'{dir}en_tok', 'r').readlines())):
    score = float(score)
    if best > score:
        best = score
        gender = genders[i % 3]
        best_de = de
        best_en = en
    if i % 3 == 2:
        predictions[gender].append(best_de.strip() + ' - ' + best_en.strip())
        best = float('inf')
        best_de = ''
        best_en = ''

with open(f'{dir}results_{model}', 'w') as file:
    for key, val in predictions.items():
        file.write(f'{key}: {len(val)}\n')
json.dump(predictions, open(f'{dir}results_{model}.json', 'w'), indent=2)









