import glob
import os
for file in glob.glob('outputs/subtitles/**/*concat22*', recursive=True):
    if 'global' not in file:
        dest = file + '_global'
        command = f'python3 -m ContraPro.evaluate --reference ContraPro/contrapro.json --scores {file} > {dest}'
        os.system(command)
