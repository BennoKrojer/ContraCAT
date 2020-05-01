import os

main_dir = 'templates/animals/'
for path, _, files in os.walk(main_dir):
    if len(files) > 1 and 'no_object' not in path:
        print(path)
        output = f'outputs/{path}'
        os.makedirs(output, exist_ok=True)
        output = output + '/concat22_pattern_match'
        command = f'python3 -m sockeye.score --target {path}/de_bpe --source {path}/en_bpe' \
                  f' --output {output}' \
                  f' --model models_dario/subtitles/concat-2-2/ --device-ids 1 --output-type score --batch-size 128'
        os.system(command)
