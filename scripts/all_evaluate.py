import glob
import os
for mod in ['but', 'true/true:no_quote']:
    for file in glob.glob(f'../ContraPro_Dario/subtitle_bpe/modified/{mod}/*'):
        if 'scores' == file:
            dest = file + '_global'
            command = f'python3 -m ContraPro.evaluate --reference ContraPro/contrapro.json --scores {file} > {dest}'
            os.system(command)
