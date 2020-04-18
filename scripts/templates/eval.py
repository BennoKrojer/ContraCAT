best = float('inf')
for i, (score, de, en) in enumerate(zip(open('../../outputs/templates/concat22', 'r'), open('../../templates/de_tok',
    'r').readlines(), open('../../templates/en_tok', 'r').readlines())):
    best = best if best < score else score
    if i % 3 == 2:
        








