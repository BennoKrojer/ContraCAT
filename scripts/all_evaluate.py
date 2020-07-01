import glob
import os
# for mod in ['true/true:_no_quote']:
for file in glob.glob(f'outputs/subtitles/nested/*/*poss_subset', recursive=True):
        dest = file + '_global'
        command = f'python3 -m ContraPro.evaluate --reference ContraPro/contrapro_possessive_subset.json --scores' \
                  f' {file} >' \
                  f' {dest}'
        os.system(command)
