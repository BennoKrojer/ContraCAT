# ATTACK GENERATION
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

python3 -m scripts.adversarial_attack.phrase_addition -n true_separate -d "es ist wahr" -e "it is true" -a --end_punct .
python3 -m scripts.adversarial_attack.phrase_addition -n and_it_true -d "und es ist wahr" -e "and it is true" -a
python3 -m scripts.adversarial_attack.phrase_addition -n and_that_true -d "und das ist wahr" -e "and that is true" -a
python3 -m scripts.adversarial_attack.phrase_addition -n true: -d "es ist wahr" -e "it is true" -p --end_punct :
python3 -m scripts.adversarial_attack.phrase_addition -n true:quot -d "es ist wahr" -e "it is true" -p --end_punct : -q

python3 -m scripts.adversarial_attack.phrase_addition -n he_said -d "er sagte" -e "he said" -p --end_punct : -q
python3 -m scripts.adversarial_attack.phrase_addition -n she_said -d "sie sagte" -e "she said" -p --end_punct : -q

python3 -m scripts.adversarial_attack.phrase_addition -n but_sure_sep -d "aber er war sich nicht sicher" -e "but he wasn't sure" -a --end_punct .
python3 -m scripts.adversarial_attack.phrase_addition -n but_sure -d "aber er war sich nicht sicher" -e "but he wasn't sure" -a --start_punct_de ,

# TEMPLATE GENERATION
python3 -m scripts.templates.generate_template -n 0_priors/position -e "I stood in front of the <ANIMAL>_1 and the <ANIMAL>_2. It was <SIZE_ADJECTIVE>." -d "Ich stand vor <DEF_DAT> <ANIMAL>_1 und <DEF_DAT> <ANIMAL>_2. <PRO_NOM_3_SIN> war <SIZE_ADJECTIVE>." --unequal_gender_entities "<ANIMAL>_1,<ANIMAL>_2" --no_correct_antecedent
python3 -m scripts.templates.generate_template -n 0_priors/role -e "The <ANIMAL> ate the <FOOD>. It was <SIZE_ADJECTIVE>." -d "<DEF_NOM> <ANIMAL> hat <DEF_ACC> <FOOD> gegessen. <PRO_NOM_3_SIN> war <SIZE_ADJECTIVE>." --unequal_gender_entities "<ANIMAL>,<FOOD>" --no_correct_antecedent
python3 -m scripts.templates.generate_template -n 0_priors/verb -e "Wow! <PRO_NOM> <TRANS_VERB> it." -d "Wow! <PRO_NOM> <TRANS_VERB> <PRO_ACC_3_SIN>."
python3 -m scripts.templates.generate_template -n 1_entity_step -e "The <ANIMAL>* and the <HUMAN> were <FEELING_ADJECTIVE>_1. However it was <FEELING_ADJECTIVE_COMP>_1.///The <HUMAN> and the <ANIMAL> were <FEELING_ADJECTIVE>_1. However it was <FEELING_ADJECTIVE_COMP>_1." -d "<DEF_NOM> <ANIMAL>* und <DEF_NOM> <HUMAN> waren <FEELING_ADJECTIVE>_1. Aber <PRO_NOM_3_SIN>* war <FEELING_ADJECTIVE_COMP>_1.///<DET_NOM> <HUMAN> und <DET_NOM> <ANIMAL>* waren <FEELING_ADJECTIVE>_1. Aber <PRO_NOM_3_SIN>* war <FEELING_ADJECTIVE_COMP>_1." --unequal_gender_entities "<ANIMAL>,<HUMAN>"
python3 -m scripts.templates.generate_template -n 2_coreference_step/event/happened -e "The <ANIMAL> ate the <FOOD>. It actually happened." -d "<DEF_NOM> <ANIMAL> hat <DEF_ACC> <FOOD> gegessen. <PRO_NOM_3_SIN> ist tatsächlich passiert." --neuter_always_correct
python3 -m scripts.templates.generate_template -n 2_coreference_step/event/chaos -e "The <ANIMAL> ate the <FOOD>. It resulted in chaos." -d "<DEF_NOM> <ANIMAL> hat <DEF_ACC> <FOOD> gegessen. <PRO_NOM_3_SIN> führte zu Chaos." --neuter_always_correct
python3 -m scripts.templates.generate_template -n 2_coreference_step/event/chaos -e "The <ANIMAL> ate the <FOOD>. It resulted in chaos." -d "<DEF_NOM> <ANIMAL> hat <DEF_ACC> <FOOD> gegessen. <PRO_NOM_3_SIN> führte zu Chaos." --neuter_always_correct
python3 -m scripts.templates.generate_template -n 2_coreference_step/event/situation -e "The <ANIMAL> ate the <FOOD>. It came as a surprise." -d "<DEF_NOM> <ANIMAL> hat <DEF_ACC> <FOOD> gegessen. <PRO_NOM_3_SIN> kam überraschend." --neuter_always_correct
python3 -m scripts.templates.generate_template -n 2_coreference_step/overlap/object_overlap -e "The <ANIMAL>_1 ate the <FOOD> and the <ANIMAL>*_2 drank the <DRINK>_3. It liked the <DRINK>_3." -d "<DEF_NOM> <ANIMAL>_1 hat <DEF_ACC> <FOOD> gegessen und <DEF_NOM> <ANIMAL>*_2 hat <DEF_ACC> <DRINK>_3 getrunken. <PRO_NOM_3_SIN> mochte <DEF_ACC> <DRINK>_3." --unequal_gender_entities "<ANIMAL>_1,<ANIMAL>*_2"
python3 -m scripts.templates.generate_template -n 2_coreference_step/overlap/object_overlap/eat_drink_drink -e "The <ANIMAL>_1 ate the <FOOD> and the <ANIMAL>*_2 drank the <DRINK>_3. It liked the <DRINK>_3." -d "<DEF_NOM> <ANIMAL>_1 hat <DEF_ACC> <FOOD> gegessen und <DEF_NOM> <ANIMAL>*_2 hat <DEF_ACC>_4 <DRINK>_3 getrunken. <PRO_NOM_3_SIN> mochte <DEF_ACC>_4 <DRINK>_3." --unequal_gender_entities "<ANIMAL>_1,<ANIMAL>*_2" --half
python3 -m scripts.templates.generate_template -n 2_coreference_step/world_knowledge -e The <ANIMAL>* ate the <FOOD>. It <ANIMAL_ATTRIBUTE>.///The <ANIMAL> ate the <FOOD>*. It <FOOD_ATTRIBUTE>. -d <DEF_NOM> <ANIMAL>* hat <DEF_ACC> <FOOD> gegessen. <PRO_NOM_3_SIN>* <ANIMAL_ATTRIBUTE>.///<DEF_NOM> <ANIMAL> hat <DEF_ACC> <FOOD>* gegessen. <PRO_NOM_3_SIN>* <FOOD_ATTRIBUTE>. --unequal_gender_entities <ANIMAL>,<FOOD>
python3 -m scripts.templates.generate_template -n 3_gender_step/big -e I saw a <CONCRETE_NOUN>*. It was big. -d Ich sah <IND_ACC> <CONCRETE_NOUN>*. <PRO_NOM_3_SIN>* war groß.

# EVALUATION:
# To evaluate simply use ContraPro's evaluate script like this:
python3 -m ContraPro.evaluate --reference PATH_TO_contrapro.json --scores scripts/example_scores

# If you want to evaluate a file that was modified with possessive-extension or synonym-replacement, you have to use a different contrapro.json:
python3 -m ContraPro.evaluate --reference data/adversarial_ContraPro/synonyms/modified_contrapro_subset.json --scores scripts/example_scores
