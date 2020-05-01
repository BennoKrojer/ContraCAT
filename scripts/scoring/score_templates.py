import os

main_dir = 'templates/animals/'
for path, _, files in os.walk(main_dir):
    if files and 'no_object' not in path:
        command = f'python3 -m sockeye.score --target {path}de_bpe --source {path}en_bpe' \
                  f' --output outputs/{path}concat22_pattern_match ' \
                  f'--model models_dario/subtitles/concat-2-2/ --device-ids 1 --output-type score --batch-size 128'
        os.system(command)
