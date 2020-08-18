python3 -m scripts.adversarial_attack.possessive_extension -n company -d "des Unternehmens" -e "the company's" --de_append --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n woman -d "von der Frau" -e "the woman's" --de_append --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n man -d "vom Mann" -e "the man's" --de_append --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n mother -d "von meiner Mutter" -e "my mother's" --de_append --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n father -d "von meinem Vater" -e "my father's" --de_append --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n dog -d "vom Hund" -e "the dog's" --de_append --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n cat -d "von der Katze" -e "the cat's" --de_append --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n doctor_male -d "vom Arzt" -e "the doctors's" --de_append --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n doctor_female -d "von der Ärztin" -e "the doctors's" --de_append --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n best_friend -d "von der Mutter meines besten Freundes" -e "of my best friend's mother" --de_append --en_append
python3 -m scripts.adversarial_attack.possessive_extension -n government -d "der Regierung" -e "the government's" --de_append --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n maria -d "Marias" -e "Maria's" --de_prepend --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n lisa -d "Lisas" -e "Lisa's" --de_prepend --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n bolsena -d "Bolsenas" -e "Bolsena's" --de_prepend --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n peter -d "Peters" -e "Peter's" --de_prepend --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n robert -d "Roberts" -e "Robert's" --de_prepend --en_prepend
python3 -m scripts.adversarial_attack.possessive_extension -n david -d "Davids" -e "David's" --de_prepend --en_prepend

#python3 -m scripts.adversarial_attack.phrase_addition -n true_separate -d "es ist wahr" -e "it is true" -a --end_punct .
#python3 -m scripts.adversarial_attack.phrase_addition -n and_it_true -d "und es ist wahr" -e "and it is true" -a
#python3 -m scripts.adversarial_attack.phrase_addition -n and_that_true -d "und das ist wahr" -e "and that is true" -a
#python3 -m scripts.adversarial_attack.phrase_addition -n true: -d "es ist wahr" -e "it is true" -p --end_punct :
#python3 -m scripts.adversarial_attack.phrase_addition -n true:quot -d "es ist wahr" -e "it is true" -p --end_punct : -q
#
#python3 -m scripts.adversarial_attack.phrase_addition -n he_said -d "er sagte" -e "he said" -p --end_punct : -q
#python3 -m scripts.adversarial_attack.phrase_addition -n she_said -d "sie sagte" -e "she said" -p --end_punct : -q
#
#python3 -m scripts.adversarial_attack.phrase_addition -n but_sure_sep -d "aber er war sich nicht sicher" -e "but he wasn't sure" -a --end_punct .
#python3 -m scripts.adversarial_attack.phrase_addition -n but_sure -d "aber er war sich nicht sicher" -e "but he wasn't sure" -a --start_punct_de ,
