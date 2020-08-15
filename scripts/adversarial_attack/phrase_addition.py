import argparse
import os
import string
import config


def add_phrase(line, args, lang):
    context, sent = line.split('<SEP>')
    context = context.strip()
    if not context:
        return '', sent

    mod = args.en if lang == 'en' else args.de
    start_punct = args.start_punct_en if lang == 'en' else args.start_punct_de
    mod += (args.end_punct + ' ') if args.end_punct else ''
    mod = start_punct + ' ' + mod
    context = '"' + context + '"' if args.quotation else context

    if args.append:
        if args.end_punct:
            context = context + mod
        else:
            if context[-1] in string.punctuation:
                context = context[:-1] + mod + context[-1]
            else:
                context = context + mod
    else:
        context = mod + context
    return context.strip() + ' ', sent


def write_modify(args):
    output = config.adversarial_data_dir / 'phrase_addition' / args.mod_name
    os.makedirs(output, exist_ok=True)

    for lang in ['de', 'en']:
        with open(config.adversarial_data_dir / (lang + '.txt'), 'r') as de_file, \
                open(output / (lang + '.txt'), 'w') as out:

            for line in de_file:
                context, sent = add_phrase(line, args, lang=lang)
                line = context + '<SEP> ' + sent
                out.write(line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mod_name', '-n', help='Name of the modification.')
    parser.add_argument('--de', '-d', help='German phrase to be added to the original context sentence.')
    parser.add_argument('--en', '-e', help='English phrase to be added to the original context sentence.')
    parser.add_argument('--append', '-a', action='store_true', help='Whether to append the phrase.',
                        default=False)
    parser.add_argument('--prepend', '-p', action='store_true', help='Whether to prepend the phrase', default=False)
    parser.add_argument('--start_punct_de', type=str, help='If phrase is appended (not as a separate sentence), '
                                                           'this punctuation is used at the start of it. For German '
                                                           'comma is often recommended.',
                        default='')
    parser.add_argument('--start_punct_en', type=str, help='If phrase is appended (not as a separate sentence), '
                                                           'this punctuation is used at the start of it. Default is '
                                                           'none.',
                        default='')
    parser.add_argument('--end_punct', type=str, required=False, help='If phrase is added as a separate sentence, '
                                                                      'this punctuation is used at the end of it.',
                        default='')
    parser.add_argument('--quotation', '-q', action='store_true', default=False, help='Puts quotation marks around '
                                                                                      'context')
    args = parser.parse_args()
    assert (args.append != args.prepend)
    write_modify(args)
