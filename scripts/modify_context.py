import os

de_path = '../ContraPro_Dario/contrapro.text.tok.prev.de.de'
en_path = '../ContraPro_Dario/contrapro.text.tok.prev.en.en'
output_de = '../ContraPro_Dario/modified/er_sagte_de_tok.txt'
output_en = '../ContraPro_Dario/modified/he_said_en_tok.txt'
with open(de_path, 'r') as de_file, open(output_de, 'w') as out:
    for line in de_file:
        line = 'er sagte ' + line
        out.write(line)

with open(en_path, 'r') as en_file, open(output_en, 'w') as out:
    for line in en_file:
        line = 'he said ' + line
        out.write(line)

command_de = 'subword-nmt apply-bpe -c ../ted_data/train/ende.bpe < ../ContraPro_Dario/modified/er_sagte_de_tok.txt > tmp_de.txt'
command_en = 'subword-nmt apply-bpe -c ../ted_data/train/ende.bpe < ../ContraPro_Dario/modified/he_said_en_tok.txt > tmp_en.txt'
os.system(command_de)
os.system(command_en)

with open('tmp_de.txt', 'r') as tmp_de, open('../ContraPro_Dario/modified/er_sagte_de_bpe.txt', 'w') as bpe_de:
    for line in tmp_de:
        line = line.replace('<@@ SE@@ P@@ >', '<SEP>')
        bpe_de.write(line)

with open('tmp_en.txt', 'r') as tmp_en, open('../ContraPro_Dario/modified/he_said_en_bpe.txt', 'w') as bpe_en:
    for line in tmp_en:
        line = line.replace('<@@ SE@@ P@@ >', '<SEP>')
        bpe_en.write(line)

os.system('rm -rf tmp_de.txt')
os.system('rm -rf tmp_en.txt')