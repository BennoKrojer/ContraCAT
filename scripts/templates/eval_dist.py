import json

gender_order = ['m','f','n']
predictions = {'first_pos': [], 'second_pos': [], 'same_antecedent': [], 'other': []}
acc_scores = []
acc_en = []
acc_de = []
genders = open('../../templates/distance/gender_combination', 'r').readlines()
for i, (score, de, en) in enumerate(zip(open('../../outputs/templates/concat22_and_dist', 'r'),
                                        open('../../templates/distance/and_de_tok', 'r').readlines(),
                                        open('../../templates/distance/and_en_tok', 'r').readlines())):

    acc_scores.append(float(score)), acc_en.append(en), acc_de.append(de)
    if i % 6 == 5:
        first_gender = genders[i-5][0]
        second_gender = genders[i][0]
        bestidx1 = acc_scores[:3].index(min(acc_scores[:3]))
        bestidx2 = acc_scores[3:].index(min(acc_scores[3:]))

        if bestidx1 == bestidx2:
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

for key, val in predictions.items():
    print(f'{key}: {len(val)}')
json.dump(predictions, open('../../outputs/templates/and_dist_results.json', 'w'), indent=2)
