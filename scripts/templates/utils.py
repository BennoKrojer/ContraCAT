def tokenize(sequence):
    for punc in ['. ', '? ', '! ']:
        return sequence.replace(punc, f'{punc} <SEP> ')


def simple_cartesian_product(set_a, set_b):
    result = []
    for i in range(0, len(set_a)):
        for j in range(0, len(set_b)):

            # for handling case having cartesian
            # prodct first time of two sets
            if type(set_a[i]) != list:
                set_a[i] = [set_a[i]]

                # coping all the members
            # of set_a to temp
            temp = [num for num in set_a[i]]

            # add member of set_b to
            # temp to have cartesian product
            temp.append(set_b[j])
            result.append(temp)

    return result


def cartesian_product(list_a, n):
    # result of cartesian product
    # of all the sets taken two at a time
    temp = list_a[0]

    # do product of N sets
    for i in range(1, n):
        temp = simple_cartesian_product(temp, list_a[i])

    return temp
