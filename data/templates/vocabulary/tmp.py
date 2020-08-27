import json
from scripts.adversarial_attack.utils import get_gender_dict

en = open('concrete_nouns_brysbaert.txt').readlines()
de = open('concrete_nouns_brysbaert_de.txt').readlines()
de_freq = json.load(open('../../../resources/open_subtitles_de_freq.json', 'r'))
en_freq = json.load(open('../../../resources/open_subtitles_en_freq.json', 'r'))
g = get_gender_dict(en_key=False)
psd = {}
for e, d in zip(en, de):
    try:
            e, d = e.strip(), d.strip()
            if d in de_freq and de_freq[d] > 30 and e in en_freq and en_freq[e] > 30 \
                    and e[-1] != 's':
                gender = g[d.lower()]
                psd[e] = {'de': d, 'gender': gender}
    except:
        continue
json.dump(psd, open('concrete_noun.json', 'w'), indent=2)
