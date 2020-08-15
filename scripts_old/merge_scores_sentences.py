scores_path = '../outputs/normal/output-concat22'

en_sent_file = open('../ContraPro/contrapro.text.en', 'r')
de_sent_file = open('../ContraPro/contrapro.text.de', 'r')
en_prev_file = open('../ContraPro/contrapro.context.en', 'r')
de_prev_file = open('../ContraPro/contrapro.context.de', 'r')

with open(scores_path, 'r') as scores_file:
    scores = [str(line.strip()) for line in scores_file]

with open('sentence_scores.csv', 'w') as result_file:
    for i, score in enumerate(scores):
        result_file.write(str(score) + ';')
        result_file.write('"'+de_prev_file.readline().strip() + '\n')
        result_file.write(de_sent_file.readline().strip() + '";')
        result_file.write('"'+ en_prev_file.readline().strip()+ '\n')
        result_file.write(en_sent_file.readline().strip() + '"\n')
