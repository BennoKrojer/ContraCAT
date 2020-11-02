# ContraCAT

This repository contains the data and scripts for the paper (ContraCAT: Contrastive Coreference Analytical Templates for Machine Translation)[xxx]



## Setup

If you just want the data for your own models and tests, you can find it under `data`.
If you want to reproduce or tweak or data generation and scoring method:

First install the requirements:
```
python3 -m venv YOUR_ENVIRONMENT_NAME
pip install -r requirements.txt
```
If you want to use all  you will need 4 external resources on which we 

## Usage
The data and scripts directory each contain two subfolders: adversarial_ContraPro and templates.
### Adversarial ContraPro
The data for each adversarial attack consists of a file for English (`en.txt`) and German (`de.txt`).
Attacks of the types possessive-extension and synonym-replacement additionally contain a modified version of the original contrapro.json, since only a subset of ContraPro was modified for these attacks.

The following three example commands show how to create the data for the three types of attacks.
phrase-addition:
...
possessive-extension:
...
synonym-replacement:
...

To evaluate the modified ContraPro data, you need to have a scores-file such as the provided `example_scores`.
Each line in that file corresponds to a line in the above mentioned `en.txt` and `de.txt`.



XXX
Mention that data creation for synonym replacement depends on GermaNet. Needs 
Cite/mention Brysbaert?
Cite/mention Alex' dict.cc file?
XXX
