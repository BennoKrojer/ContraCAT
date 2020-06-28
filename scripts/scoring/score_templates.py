import os

main_dir = 'templates/0_priors/role_variant'
models = {'tuned_lowest': '/mounts/data/proj/dario/CtxTfNMTOld/models/subtitles/benno/augmentation-it-mod-lowest'}
for model, model_path in models.items():
    for path, _, files in os.walk(main_dir):
        if 'de_bpe' in files:
            print(path)
            command = f'python3 -m sockeye.score --target {path}/de_bpe --source {path}/en_bpe' \
                      f' --output {path}/scores_{model}' \
                      f' --model {model_path} --device-ids 1 --output-type score --batch-size 128'
            os.system(command)
