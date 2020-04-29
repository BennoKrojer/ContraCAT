#python3 -m sockeye.score --target templates/distance/de_bpe --source templates/distance/en_bpe --output outputs/templates/concat22_dist --model models_dario/subtitles/concat-2-2/ --device-ids 0 --output-type score --batch-size 128
python3 -m sockeye.score --target templates/animals/de_bpe --source templates/animals/en_bpe --output outputs/templates/concat22_pattern_match --model models_dario/subtitles/concat-2-2/ --device-ids 1 --output-type score --batch-size 128

