import json

predictions = {'same_position': [], 'same_antecedent': []}
acc_scores = []
acc_en = []
acc_de = []
for i, (score, de, en) in enumerate(zip(open('../../outputs/templates/concat22_dist', 'r'),
                                        open('../../templates/distance/de_tok', 'r').readlines(),
                                        open('../../templates/distance/en_tok', 'r').readlines())):

    acc_scores.append(float(score)), acc_en.append(en), acc_de.append(de)
    if i % 6 == 5:
        bestidx1 = acc_scores[:3].index(min(acc_scores[:3]))
        bestidx2 = acc_scores[3:].index(min(acc_scores[3:]))
        if bestidx1 == bestidx2:
            predictions['same_antecedent'].append(
                acc_de[bestidx1].strip() + '///' + acc_de[3:][bestidx2].strip())
        else:
            predictions['same_position'].append(
                acc_de[bestidx1].strip() + '///' + acc_de[3:][bestidx2].strip())
        acc_scores, acc_en, acc_de = [], [], []

for key, val in predictions.items():
    print(f'{key}: {len(val)}')
json.dump(predictions, open('../../outputs/templates/dist_results.json', 'w'), indent=2)
