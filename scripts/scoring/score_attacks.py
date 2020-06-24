import os

# modifications = ['but', 'true:_no_quote', 'woman', 'best_friend', 'company', 'maria', 'male', 'female',
#            'neutral']
model_path = '/mounts/data/proj/dario/CtxTfNMTOld/models/subtitles/benno/'
models = ["augmentation-synonym-mod-low","augmentation-synonym-mod-lower","augmentation-synonym-mod-lowest",
          "augmentation-it-mod-low","augmentation-it-mod-lower","augmentation-it-mod-lowest",
          "augmentation-it-nomod-low","augmentation-it-nomod-lower","augmentation-it-nomod-lowest"]

main_dir = 'ContraPro_Dario/subtitle_bpe'
for model in models:
    os.makedirs(f'{main_dir}/{model}', exist_ok=True)
    command = f'python3 -m sockeye.score --target {main_dir}/de_bpe.txt --source {main_dir}/en_bpe.txt' \
              f' --output {main_dir}/{model}/scores' \
              f' --model  {model_path}/{model}/ --device-ids 1 --output-type score --batch-size 128'

    os.system(command)
