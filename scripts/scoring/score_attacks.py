import os

include = ['but_1sent', 'true:_no_quote', 'woman', 'best_friend', 'company', 'maria', 'male_de', 'female_de',
           'neutral_de']
model_path = '/mounts/data/proj/dario/CtxTfNMTOld/models/subtitles/benno/'
models = ["augmentation-synonym-mod-low","augmentation-synonym-mod-lower","augmentation-synonym-mod-lowest",
          "augmentation-it-mod-low","augmentation-it-mod-lower","augmentation-it-mod-lowest",
          "augmentation-it-nomod-low","augmentation-it-nomod-lower","augmentation-it-nomod-lowest"]

main_dir = 'ContraPro_Dario/subtitle_bpe/modified'
for path, _, files in os.walk(main_dir):
    print(path)
    valid = False
    en = ''
    de = ''
    for x in include:
        for f in files:
            if x in f:
                valid = True
                if "de_bpe" in f:
                    de = f
                elif "en_bpe" in f:
                    en = f
    if valid:
        for model in models:
            os.makedirs(f'{path}/{model}', exist_ok=True)
            command = f'python3 -m sockeye.score --target {path}/{de} --source {path}/{en}' \
                      f' --output {path}/{model}/scores' \
                      f' --model  {model_path}/{model}/ --device-ids 1 --output-type score --batch-size 128'
            os.system(command)
