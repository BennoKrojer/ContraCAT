import glob

for file in glob.glob('../baseline_sentence_level/**/*_bpe', recursive=True):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    new = []
    for line in lines:
        _, main = line.split('<SEP> ')
        new.append(main)
    with open(file, 'w') as f:
        f.write(''.join(new))