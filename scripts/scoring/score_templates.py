import os

main_dir = 'templates_SEP_fixed/'
for path, _, files in os.walk(main_dir):
    if len(files) == 5:
        print(path)
        command = f'python3 -m sockeye.score --target {path}/de_bpe --source {path}/en_bpe' \
                  f' --output {path}/concat22' \
                  f' --model models_dario/subtitles/concat-2-2/ --device-ids 1 --output-type score --batch-size 128'
        os.system(command)
