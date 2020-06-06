from collections import defaultdict
import json

freq_dict = defaultdict(int)

with open('OpenSubtitles.de-en.clean.train.tok.clean.de') as file:
    for line in file:
        tokens = [token for token in line.split() if token.isalpha()]
        for token in tokens:
            freq_dict[token] += 1
freq_dict = dict(sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)[:200000])
json.dump(freq_dict, open('open_subtitles_de_freq.json', 'w'), indent=2, ensure_ascii=False)
