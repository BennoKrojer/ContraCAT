# ContraCAT

This repository contains the data and scripts for the paper [ContraCAT: Contrastive Coreference Analytical Templates for Machine Translation](https://sites.google.com/view/contracat/).

## Setup

If you just want the data for your own models and tests, you can find it under `data`.
Go to `scripts` to reproduce or tweak or data generation and evaluation method.

First install the requirements:
```
python3 -m venv YOUR_ENVIRONMENT_NAME
pip install -r requirements.txt
```
If you want to reproduce or modify our data generation, you also need 3 external resources:
1. ContraPro
2. GermaNet
3. some form of mapping from German noun to gender
Details for each are further down.

## Usage
The data and scripts directory each contain two subfolders: adversarial_ContraPro and templates.
If you quickly want to look at commands to reproduce our data generation, go to `commands.sh`.
### Adversarial ContraPro
The data for each adversarial attack consists of a file for English (`en.txt`) and German (`de.txt`).
Attacks of the types possessive-extension and synonym-replacement additionally contain a modified version of the original `contrapro.json`, since only a subset of ContraPro was modified for these attacks. This means we only want to evaluate on that subset.

The following three example commands show how to create the data for the three types of attacks.
```
python3 -m scripts.adversarial_attack.phrase_addition -n true_separate -d "es ist wahr" -e "it is true" -a --end_punct .
python3 -m scripts.adversarial_attack.possessive_extension -n david -d "Davids" -e "David's" --de_prepend --en_prepend`
python3 -m scripts.adversarial_attack.synonym_replacement
```

### Templates
The data for our ContraCAT templaes is under `data/templates` and is further semantically divided into the different steps of coreference.
On the lowest level, each concrete template consists of `en.txt` and `de.txt` file, as well as a groundtruth file called `gender.txt`.
To generate the template, you call `scripts/generate_template.py`, e.g.:

`python3 -m scripts.templates.generate -n 0_priors/verb -e "Wow! <PRO_NOM> <TRANS_VERB> it." -d "Wow! <PRO_NOM> <TRANS_VERB> <PRO_ACC_3_SIN>."`

(for more details see `commands.sh`)

### Scoring and evaluation
To evaluate the attacks or templates, you need to have a scores-file such as the provided `example_scores`.
Such a score-file can be created e.g. with XXX (Dario, what to say here ideally?)
Each line in that file corresponds to a line in the above mentioned `en.txt` and `de.txt`.
These scores are then evaluated with two scripts.

For adversarial attacks, we call the original ContraPro evaluation, e.g.:

`python3 -m ContraPro.evaluate --reference PATH_TO_contrapro.json --scores scripts/example_scores`
For possessive extension and synonym replacement the reference json-file has to be a subset,e.g.:

`python3 -m ContraPro.evaluate --reference data/adversarial_ContraPro/synonyms/modified_contrapro_subset.json --scores scripts/example_scores`

For the evaluation of templates, simply call our script `scripts/templates/evaluate.py`.

## Dependencies for adversarial attack generation
1. ContraPro: Simply clone the [ContraPro repo](https://github.com/ZurichNLP/ContraPro) into the project directory.
2. GermaNet: this was needed to get a mapping from an English to a German synset (find access [here](https://uni-tuebingen.de/en/142806)). You will have to change the path in `config.py` if you download it.
3. noun-to-gender-mapping: we cannot provide this mapping and you will have to implement `get_gender_dict()` in `utils.py` on your own.

## Citation
