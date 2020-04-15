python3 -m sockeye.score --target ContraPro_Dario/modified/but/aber_1sent_de_bpe.txt --source ContraPro_Dario/modified/but/but_1sent_en_bpe.txt --output outputs/subtitles/but/concat22_1sent --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/but/aber_de_bpe.txt --source ContraPro_Dario/modified/but/but_en_bpe.txt --output outputs/subtitles/but/concat22 --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/catch/haken_1sent_de_bpe.txt --source ContraPro_Dario/modified/catch/catch_1sent_en_bpe.txt --output outputs/subtitles/catch/concat22_1sent --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/catch/haken_de_bpe.txt --source ContraPro_Dario/modified/catch/catch_en_bpe.txt --output outputs/subtitles/catch/concat22 --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/noun_phrases/father_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/noun_phrases/father_no_mismatches_en_bpe.txt --output outputs/nested/noun_phrases/concat22_father --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/noun_phrases/female_doctor_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/noun_phrases/female_doctor_no_mismatches_en_bpe.txt --output outputs/nested/noun_phrases/concat22_female_doctor --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/noun_phrases/male_doctor_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/noun_phrases/male_doctor_no_mismatches_en_bpe.txt --output outputs/nested/noun_phrases/concat22_male_doctor --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/noun_phrases/man_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/noun_phrases/man_no_mismatches_en_bpe.txt --output outputs/nested/noun_phrases/concat22_man --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/noun_phrases/mother_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/noun_phrases/mother_no_mismatches_en_bpe.txt --output outputs/nested/noun_phrases/concat22_mother --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/noun_phrases/woman_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/noun_phrases/woman_no_mismatches_en_bpe.txt --output outputs/nested/noun_phrases/concat22_woman --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/noun_phrases/best_friend_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/noun_phrases/best_friend_no_mismatches_en_bpe.txt --output outputs/nested/noun_phrases/concat22_best_friend --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/noun_phrases/dog_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/noun_phrases/dog_no_mismatches_en_bpe.txt --output outputs/nested/noun_phrases/concat22_dog --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/noun_phrases/cat_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/noun_phrases/cat_no_mismatches_en_bpe.txt --output outputs/nested/noun_phrases/concat22_cat --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/names/bolsena_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/names/bolsena_no_mismatches_en_bpe.txt --output outputs/nested/names/concat22_bolsena --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/names/david_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/names/david_no_mismatches_en_bpe.txt --output outputs/nested/names/concat22_david --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/names/lisa_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/names/lisa_no_mismatches_en_bpe.txt --output outputs/nested/names/concat22_lisa --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/names/maria_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/names/maria_no_mismatches_en_bpe.txt --output outputs/nested/names/concat22_maria --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/names/peter_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/names/peter_no_mismatches_en_bpe.txt --output outputs/nested/names/concat22_peter --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/nested/names/robert_no_mismatches_de_bpe.txt --source ContraPro_Dario/modified/nested/names/robert_no_mismatches_en_bpe.txt --output outputs/nested/noun_phrases/concat22_robert --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/point/punkt_1sent_de_bpe.txt --source ContraPro_Dario/modified/point/point_1sent_en_bpe.txt --output outputs/subtitles/point/concat22_1sent --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/point/punkt_de_bpe.txt --source ContraPro_Dario/modified/point/point_en_bpe.txt --output outputs/subtitles/point/concat22 --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/synonyms/same_gender/same_gender_de_bpe.txt --source ContraPro_Dario/modified/synonyms/same_gender/same_gender_en_bpe.txt --output outputs/subtitles/synonyms/same_gender/concat22 --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/synonyms/male/male_de_bpe.txt --source ContraPro_Dario/modified/synonyms/male/male_en_bpe.txt --output outputs/subtitles/synonyms/male/concat22 --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/synonyms/female/female_de_bpe.txt --source ContraPro_Dario/modified/synonyms/female/female_en_bpe.txt --output outputs/subtitles/synonyms/female/concat22 --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/synonyms/neutral/neutral_de_bpe.txt --source ContraPro_Dario/modified/synonyms/neutral/neutral_en_bpe.txt --output outputs/subtitles/synonyms/neutral/concat22 --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/why/wieso_1sent_de_bpe.txt --source ContraPro_Dario/modified/why/why_1sent_en_bpe.txt --output outputs/subtitles/why/concat22_1sent --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128
python3 -m sockeye.score --target ContraPro_Dario/modified/why/wieso_de_bpe.txt --source ContraPro_Dario/modified/why/why_en_bpe.txt --output outputs/subtitles/why/concat22 --model models_dario/ted/concat-2-2/ --device-ids 1 --output-type score --batch-size 128