import json

best = float('inf')
genders = ['er', 'sie', 'es']
predictions = {'er': [], 'sie': [], 'es': []}
best_en = ''
best_de = ''
for i, (score, de, en) in enumerate(zip(open('../../outputs/templates/concat22_trans', 'r'),
                                        open('../../templates/transitive/de_tok', 'r').readlines(),
                                        open('../../templates/transitive/en_tok', 'r').readlines())):
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

for key, val in predictions.items():
    print(f'{key}: {len(val)}')
json.dump(predictions, open('../../outputs/templates/trans_results.json', 'w'), indent=2)









