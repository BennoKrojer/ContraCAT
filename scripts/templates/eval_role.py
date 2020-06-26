import json

gender_order = ['m', 'f', 'n']
predictions = {'subj': [], 'obj': [], 'other': []}
acc_scores = []
acc_en = []
acc_de = []
model = 'tuned_lowest'
dir = '../../templates/final/0_priors/position/'
genders = open(f'{dir}gender_combination', 'r').readlines()
for i, (score, de, en) in enumerate(zip(open(f'{dir}scores_{model}', 'r'),
                                        open(f'{dir}de_tok', 'r').readlines(),
                                        open(f'{dir}en_tok', 'r').readlines())):

    acc_scores.append(float(score)), acc_en.append(en), acc_de.append(de)
    if i % 3 == 2:
        first_gender, second_gender = genders[i][0], genders[i][1]
        pred_gender_i = acc_scores.index(min(acc_scores))
        pred_gender = gender_order[pred_gender_i]

        if first_gender == pred_gender:
            predictions['subj'].append(
                acc_de[pred_gender_i].strip())
        elif second_gender == pred_gender:
            predictions['obj'].append(
                acc_de[pred_gender_i].strip())
        else:
            predictions['other'].append(
                acc_de[pred_gender_i].strip())
        acc_scores, acc_en, acc_de = [], [], []

with open(f'{dir}results_{model}', 'w') as file:
    for key, val in predictions.items():
        file.write(f'{key}: {len(val)}\n')
json.dump(predictions, open(f'{dir}results_{model}.json', 'w'), indent=2)
