best = float('inf')
genders = ['er', 'sie', 'es']
for i, (score, de, en) in enumerate(zip(open('../../outputs/templates/concat22', 'r'), open('../../templates/de_tok',
    'r').readlines(), open('../../templates/en_tok', 'r').readlines())):
    if best > score:
        best = score
        gender = genders[i%3]
    if i % 3 == 2:










