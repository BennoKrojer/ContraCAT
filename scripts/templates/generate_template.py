from argparse import ArgumentParser
import json
import re
import config
from scripts.templates.utils import cartesian_product

class Entity:
    def __init__(self, en, de, gender=None):
        self.de = de
        self.en = en
        self.gender = gender

class Template:

    def __init__(self, string):
        self.string = string
        self.tokens = []
        self.sampling_slots = []

    def __str__(self):
        return self.string


class Token:

    def __init__(self, idx, string, token_type, lang, potential_antecedent=False, antecedent=False):
        self.idx = idx
        self.string = string
        self.token_type = token_type
        self.lang = lang
        self.potential_antecedent = potential_antecedent
        self.antecedent = antecedent

    def __str__(self):
        return self.string


def load_entities(entity_type):
    entities = json.load(open(config.template_data_dir / 'universe' / entity_type.lower() + '.json'))
    for en, de in entities.items():



def parse(template_str, lang):
    antecedent_token, referring_pronoun = None, None
    template = Template(template_str)
    for i, token_str in enumerate(template_str.split()):
        if '<' and '>' in token_str:
            potential_antecedent = 'ANIMAL' in token_str or 'HUMAN' in token_str or 'FOOD' in token_str or 'DRINK' in token_str
            antecedent = '>!' in token_str and potential_antecedent
            if potential_antecedent:
                type = 'entity_slot'
            elif token_str == '<PRO_NOM_3_SIN>*':
                type = 'referring_slot'
            elif '<DEF' in token_str or '<IND' in token_str:
                type = 'gender_dependent_slot'
            else:
                type = 'other_slot'
            token = Token(i, token_str, token_type=type, lang=lang, potential_antecedent=potential_antecedent,
                          antecedent=antecedent)
            if antecedent:
                template.antecedent_token = token

        else:
            token = Token(i, token_str, token_type='literal', lang=lang)
        if token_str[-1] in ['.', '!', '?']:
            template.tokens.append('<SEP>')
        template.tokens.append(token)

    for i, token in enumerate(template.tokens):
        if token.token_type == 'reffering_slot':
            referring_pronoun = token
            template.referring_pronoun = token
            antecedent_token.referred_by = referring_pronoun
            referring_pronoun.referrring_to = antecedent_token
        if token.token_type in ['entity_slot', 'other_slot']:
            template.sampling_slots.append(token)
        if token.token_type == 'gender_dependent_slot':
            token.gender_dependency = template.tokens[i + 1]
    # connect slots that are not allowed to have same gender; use it later when filtering the cartesian product
    to_remove = []
    new_slots = []
    for i, slot in enumerate(template.sampling_slots):
        if slot.string[-1].isdigit():
            entity_id = slot.string[-1]
            for slot_2 in template.sampling_slots[i + 1:]:
                if slot_2.string[-1] == entity_id:
                    slot.same_entity = slot_2
                    to_remove.append(slot_2)
        if slot not in to_remove:
            new_slots.append(slot)

    template.sampling_slots = new_slots
    return template


def combine(sampling_slots):
    sets = []
    for slot in sampling_slots:
        key = re.split('[<>]', slot.string)[1]
        entity_set = load_entities(key)
        sets.append(entity_set)
    
    cartesians = cartesian_product(sets, len(sets))
    #implement filter to remove combinations where gender is the same where it shouldn't be

    return cartesians



def main(args):
    en_template = parse(args.en_template, lang='en')
    de_template = parse(args.de_template, lang='de')
    combinations = combine(en_template.sampling_slots)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--en_template', '-e', required=True, type=str,
                        help='The English template with variables/slots for entities to be filled. For more details '
                             'see README.')
    parser.add_argument('--de_template', '-d', required=True, type=str,
                        help='The German template with variables/slots for entities to be filled. For more details '
                             'see '
                             'README.')
    parser.add_argument('--unequal_gender_entities', type=str,
                        help='State the variables/slots that are not allowed to have the same gender when filling the '
                             '2 (or more slots). Separate by comma, e.g.: "<ANIMAL>_1,<FOOD>_1')
    parser.add_argument('--neuter_always_correct', action='store_true', required=False,
                        help='Whether the correct pronoun should always be neuter. This is used for pleonastic/event '
                             'references so far.')
    args = parser.parse_args()
    main(args)
