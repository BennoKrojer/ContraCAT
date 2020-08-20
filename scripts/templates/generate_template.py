import os
import sys
from argparse import ArgumentParser
import json
import re

import config
from scripts.templates.utils import cartesian_product

VALID_VARIABLES = ['ANIMAL', 'HUMAN', 'FOOD', 'DRINK', 'DEF_NOM', 'IND_NOM', 'DEF_ACC', 'PRO_NOM', 'PRO_NOM_3_SIN',
                   'PRO_ACC_3_SIN', 'SIZE_ADJECTIVE', 'FEELING_ADJECTIVE', 'FEELING_ADJECTIVE_COMP', 'TRANS_VERB',
                   'ADVERB']


def get_declination(string, key=None, lang='de'):
    if lang == 'de':
        if string == '<PRO_NOM_3_SIN>':
            return {'m': 'er', 'f': 'sie', 'n': 'es'}
        if string == '<PRO_ACC_3_SIN>':
            return {'m': 'ihn', 'f': 'sie', 'n': 'es'}
        if string == '<DEF_NOM>':
            return {'m': 'der', 'f': 'die', 'n': 'das'}[key]
        if string == '<DEF_ACC>':
            return {'m': 'den', 'f': 'die', 'n': 'das'}[key]
        if string == '<DEF_DAT>':
            return {'m': 'dem', 'f': 'der', 'n': 'dem'}[key]
        if string == '<FEELING_ADJECTIVE_COMP>':
            return {'hungrig': 'hungriger', 'müde': 'müder', 'glücklich': 'glücklicher', 'nett': 'netter'}[key]
        if string == 'HABEN':
            return {'I': 'habe', 'you': 'hast', 'he': 'hat', 'she': 'hat', 'we': 'haben', 'they': 'haben'}[key]
    elif lang == 'en':
        if string == '<FEELING_ADJECTIVE_COMP>':
            return {'hungry': 'hungrier', 'tired': 'more tired', 'happy': 'happier', 'nice': 'nicer'}[key]


class Entity:
    def __init__(self, en, de, entity_type, gender=None):
        self.de = de
        self.en = en
        self.gender = gender
        self.entity_type = entity_type

    def __str__(self):
        return f'{self.en} / {self.de}'

    def __eq__(self, other):
        if self.de == other.de and self.en == other.en:
            return True
        else:
            return False


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
        self.current_value = None
        self.same_entity = None

    def __str__(self):
        return self.string


def load_entities(entity_type, args):
    entities = json.load(open(config.template_data_dir / 'universe' / (entity_type.lower() + '.json')))
    new_entities = []
    if args.full.lower() == entity_type.lower():
        entities = entities.items()
    else:
        entities = list(entities.items())[::2 if args.half else 1]
    for en, de in entities:
        if entity_type.lower() == 'human':
            for gender, de_str in de.items():
                new_entities.append(Entity(en, de_str, entity_type, gender=gender))
        elif type(de) == dict:
            new_entities.append(Entity(en, de['de'], entity_type, gender=de['gender']))
        elif type(de) == str:
            new_entities.append(Entity(en, de, entity_type))
        elif type(de) == list:
            for word in de:
                new_entities.append(Entity(en, word, entity_type))
    return new_entities


def check_valid(token_str):
    token = re.split('[<>]', token_str)[1]
    if token not in VALID_VARIABLES:
        raise ValueError(f'The variable name {token_str} you used in the template in is not defined and can therefore '
                         f'not be '
                         'filled.')


def parse(template_str, args, lang):
    unequal_entities_str = args.unequal_gender_entities.split(',')
    unequal_entities = []
    antecedent_token, referring_pronoun = None, None
    template = Template(template_str)
    offset = 0
    for i, token_str in enumerate(template_str.split()):
        later = []
        if token_str[-1] in ['.', '!', '?']:
            later.append(token_str[-1])
            if i != len(template_str.split()) - 1:
                later.append('<SEP>')
            token_str = token_str[:-1]

        if '>' in token_str and '<' in token_str:
            check_valid(token_str)
            potential_antecedent = 'ANIMAL' in token_str or 'HUMAN' in token_str or 'FOOD' in token_str or 'DRINK' in token_str
            antecedent = '>*' in token_str and potential_antecedent
            if potential_antecedent:
                type = 'entity_slot'
            elif token_str in ['<PRO_NOM_3_SIN>*', 'PRO_ACC_3_SIN>*']:
                type = 'referring_slot'
            elif '<DEF' in token_str or '<IND' in token_str:
                type = 'gender_dependent_slot'
            else:
                type = 'other_slot'
            token = Token(i + offset, token_str, token_type=type, lang=lang, potential_antecedent=potential_antecedent,
                          antecedent=antecedent)
            if antecedent:
                template.antecedent_token = token

        else:
            token = Token(i + offset, token_str, token_type='literal', lang=lang)
        for e in unequal_entities_str:
            e = e.strip()
            if '<' in e and '>' in e and e in token_str:
                unequal_entities.append(token)
        template.tokens.append(token)
        for j, token in enumerate(later):
            template.tokens.append(Token(i + j + 1, token, token_type='literal', lang=lang))
            offset = j + 1
    template.unequal_entities = unequal_entities

    for i, token in enumerate(template.tokens):
        if token.token_type == 'referring_slot':
            referring_pronoun = token
            template.referring_pronoun = token
            template.antecedent_token.referred_by = referring_pronoun
            referring_pronoun.referrring_to = antecedent_token
        if token.token_type in ['entity_slot', 'other_slot']:
            template.sampling_slots.append(token)
        if token.token_type == 'gender_dependent_slot':
            token.gender_dependency = template.tokens[i + 1]

    to_remove = []
    new_slots = []
    for i, slot in enumerate(template.tokens):
        if slot.string[-1].isdigit():
            entity_id = slot.string[-1]
            for slot2 in template.tokens[i + 1:]:
                if slot2.string[-1] == entity_id:
                    slot.same_entity = slot2
                    slot2.same_entity = slot
                    if slot2 in template.sampling_slots:
                        to_remove.append(slot2)
        if slot in template.sampling_slots and slot not in to_remove:
            new_slots.append(slot)

    template.sampling_slots = new_slots
    return template


def combine(template, args):
    sets = []
    gender_constrained_idx = []
    for i, slot in enumerate(template.sampling_slots):
        key = re.split('[<>]', slot.string)[1]
        entity_set = load_entities(key, args)
        sets.append(entity_set)
        if slot in template.unequal_entities:
            gender_constrained_idx.append(i)
    cartesians = cartesian_product(sets, len(sets))
    # implement filter to remove combinations where gender is the same where it shouldn't be
    new_cartesians = []
    for tuple in cartesians:
        constrained_entities = [e for i, e in enumerate(tuple) if i in gender_constrained_idx]
        genders = []
        satisfied = True
        for e in constrained_entities:
            if e.gender in genders:
                satisfied = False
            genders.append(e.gender)
        for i, e1 in enumerate(tuple):
            for e2 in tuple[i + 1:]:
                if e1.entity_type == e2.entity_type and str(e1) == str(e2):
                    satisfied = False
        if satisfied:
            if tuple not in new_cartesians:
                new_cartesians.append(tuple)
            if len(constrained_entities) == 2:
                first = tuple.index(constrained_entities[0])
                second = tuple.index(constrained_entities[1])
                swapped_tuple = tuple.copy()
                swapped_tuple[first], swapped_tuple[second] = swapped_tuple[second], swapped_tuple[first]
                if swapped_tuple in cartesians and swapped_tuple not in new_cartesians:
                    new_cartesians.append(swapped_tuple)
    return new_cartesians


def write_templates(en_template, de_template, combinations, args, write_mode):
    path = config.template_data_dir
    for name in args.template_name.split('/'):
        path = path / name
    os.makedirs(path, exist_ok=True)
    with open(path / 'en.txt', write_mode) as en_file, open(path / 'de.txt', write_mode) as de_file, \
            open(path / 'genders.txt', write_mode) as gender_file:
        for combination in combinations:
            combination_copy = combination.copy()
            en_phrase = ''
            for i, token in enumerate(en_template.tokens):
                if token.token_type == 'literal':
                    word = token.string + ' '
                elif token.token_type in ['entity_slot', 'other_slot']:
                    if token.same_entity and token.same_entity.current_value:
                        if token.string == token.same_entity.string:
                            word = token.same_entity.current_value + ' '
                        else:
                            word = get_declination(token.string[:-2], key=token.same_entity.current_value,
                                                   lang='en') + ' '
                    else:
                        word = combination_copy[0].en + ' '
                        combination_copy.pop(0)
                        token.current_value = word.strip()
                en_phrase += word.capitalize() if en_template.tokens[i - 1].string == '<SEP>' else word
            en_phrase = en_phrase.strip()
            en_phrase = en_phrase[0].upper() + en_phrase[1:]
            for punct in ['.', '!', '?']:
                en_phrase = en_phrase.replace(' ' + punct, punct)
            for _ in range(3):
                en_file.write(en_phrase + '\n')

            for g in ['m', 'f', 'n']:
                de_phrase = ''
                gender_combination = ''
                combination_copy = combination.copy()
                waiting_token = ''
                for i, token in enumerate(de_template.tokens):
                    if token.token_type == 'literal':
                        word = token.string + ' '
                    elif '<PRO_NOM_3_SIN>' in token.string:
                        mapping = get_declination('<PRO_NOM_3_SIN>')
                        word = mapping[g] + ' '
                    elif '<PRO_ACC_3_SIN>' in token.string:
                        mapping = get_declination('<PRO_ACC_3_SIN>')
                        word = mapping[g] + ' '
                        if waiting_token:
                            word += waiting_token + ' '
                    elif token.token_type in ['entity_slot', 'other_slot']:
                        if token.string == '<PRO_NOM>':
                            waiting_token = combination_copy[0].en
                        if (args.no_correct_antecedent and token.potential_antecedent) or token.antecedent:
                            gender_combination += combination_copy[0].gender
                        elif args.neuter_always_correct:
                            gender_combination = 'n'
                        if token.string == '<TRANS_VERB>':
                            verb = combination_copy[0].de
                            if len(verb.split()) == 2:
                                word = get_declination('HABEN', waiting_token) + ' '
                                waiting_token = verb.split()[1]
                            combination_copy.pop(0)
                        elif token.same_entity and token.same_entity.current_value:
                            if token.string == token.same_entity.string:
                                word = token.same_entity.current_value + ' '
                            else:
                                word = get_declination(token.string[:-2], key=token.same_entity.current_value,
                                                       lang='de') + ' '
                        else:
                            word = combination_copy[0].de + ' '
                            combination_copy.pop(0)
                            token.current_value = word.strip()
                    elif token.token_type == 'gender_dependent_slot':
                        if token.same_entity and token.same_entity.current_value:
                            word = token.same_entity.current_value + ' '
                        else:
                            gender = combination_copy[0].gender
                            literal = get_declination(token.string[:-2] if token.string[-2] == '_' else token.string,
                                                      gender)
                            word = literal + ' '
                            token.current_value = word.strip()
                    de_phrase += word.capitalize() if i != 0 and de_template.tokens[i - 1].string == '<SEP>' else word
                de_phrase = de_phrase.strip()
                de_phrase = de_phrase[0].upper() + de_phrase[1:]
                for punct in ['.', '!', '?']:
                    de_phrase = de_phrase.replace(' ' + punct, punct)
                gender_file.write(gender_combination + '\n')
                de_file.write(de_phrase + '\n')
    with open(path / 'commandline_args.txt', 'w') as f:
        f.write('\n'.join(sys.argv[1:]))


def main(args):
    for i, (en_template, de_template) in enumerate(zip(args.en_template.split('///'), args.de_template.split('///'))):
        en_template = parse(en_template, args, lang='en')
        de_template = parse(de_template, args, lang='de')
        combinations = combine(en_template, args)
        write_templates(en_template, de_template, combinations, args, 'w' if i == 0 else 'a')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--template_name', '-n', required=True, help='Can also be split by / to create path with '
                                                                     'directories.')
    parser.add_argument('--en_template', '-e', required=True, type=str,
                        help='The English template with variables/slots for entities to be filled. For more details '
                             'see README.')
    parser.add_argument('--de_template', '-d', required=True, type=str,
                        help='The German template with variables/slots for entities to be filled. For more details '
                             'see '
                             'README.')
    parser.add_argument('--unequal_gender_entities', type=str, default='',
                        help='State the variables/slots that are not allowed to have the same gender when filling the '
                             '2 (or more slots). Separate by comma, e.g.: "<ANIMAL>_1,<FOOD>_1')
    parser.add_argument('--neuter_always_correct', action='store_true', required=False,
                        help='Whether the correct pronoun should always be neuter. This is used for pleonastic/event '
                             'references so far.')
    parser.add_argument('--no_correct_antecedent', action='store_true',
                        help='You can create templates that analyze priors and do not have a correct antecedent. For '
                             'these the groundtruth file will look different')
    parser.add_argument('--half', action='store_true',
                        help='Reduces size of resulting sequences by only using half of all involved entities')
    parser.add_argument('--full', default='',
                        help='Honestly: A quick-fix to make the --half parameter more specific. The passed slots are '
                             'used fully.')
    args = parser.parse_args()
    main(args)
