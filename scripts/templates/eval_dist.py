import json

gender_order = ['m', 'f', 'n']
predictions = {'first_pos': [], 'second_pos': [], 'same_antecedent': [], 'other': []}
acc_scores = []
acc_en = []
acc_de = []
model = 'tuned'
dir = '../../templates/final/0_priors/position/'
genders = open(f'{dir}gender_combination', 'r').readlines()
for i, (score, de, en) in enumerate(zip(open(f'{dir}scores_{model}', 'r'),
                                        open(f'{dir}de_tok', 'r').readlines(),
                                        open(f'{dir}en_tok', 'r').readlines())):

    acc_scores.append(float(score)), acc_en.append(en), acc_de.append(de)
    if i % 6 == 5:
        first_gender = genders[i-5][0]
        second_gender = genders[i][0]
        bestidx1 = acc_scores[:3].index(min(acc_scores[:3]))
        bestidx2 = acc_scores[3:].index(min(acc_scores[3:]))

        if bestidx1 == bestidx2 and (gender_order[bestidx2] == second_gender or gender_order[bestidx2] == first_gender):
            predictions['same_antecedent'].append(
                acc_de[bestidx1].strip() + '///' + acc_de[3:][bestidx2].strip())
        elif bestidx1 == gender_order.index(first_gender) and bestidx2 == gender_order.index(second_gender):
            predictions['first_pos'].append(
                acc_de[bestidx1].strip() + '///' + acc_de[3:][bestidx2].strip())
        elif bestidx1 == gender_order.index(second_gender) and bestidx2 == gender_order.index(first_gender):
            predictions['second_pos'].append(
                acc_de[bestidx1].strip() + '///' + acc_de[3:][bestidx2].strip())
        else:
            predictions['other'].append(
                acc_de[bestidx1].strip() + '///' + acc_de[3:][bestidx2].strip())
        acc_scores, acc_en, acc_de = [], [], []

with open(f'{dir}results_{model}', 'w') as file:
    for key, val in predictions.items():
        file.write(f'{key}: {len(val)}\n')
json.dump(predictions, open(f'{dir}results_{model}.json', 'w'), indent=2)
