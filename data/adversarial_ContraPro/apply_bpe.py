import os
from glob import glob

for file in glob('modified/**/*tok*', recursive=True):
    print(file)
    dest = file.replace('tok', 'bpe')

    command = f'subword-nmt apply-bpe -c ../../models_dario/subtitles/ende.bpe --glossaries "<SEP>" < ' \
              f'{file} > {dest}'
    os.system(command)