# from nltk.metrics.distance import edit_distance
#
# with open('../ContraPro_Dario/contrapro.text.tok.de', 'r') as file:
#     group_sizes = []
#     count = 1
#     lines = file.readlines()
#     for i in range(len(lines)-1):
#         print(i)
#         if edit_distance(lines[i], lines[i+1]) < 10:
#             count += 1
#         else:
#             group_sizes.append((i+1-count, i+1))
#             count = 1
#
# with open('../ContraPro_Dario/sentence_groups.txt', 'w') as file:
#     for n in group_sizes:
#         file.write(str(n[0]) + ' ' + str(n[1]) + '\n')

import json

reference = json.load(open('../ContraPro/contrapro.json', 'r'))
with open('../ContraPro_Dario/sentence_groups.txt', 'w') as file:
    count = 0
    file.write('0\n')
    for example in reference:
        count = count + len(example['errors']) + 1
        file.write(str(count) + '\n')
