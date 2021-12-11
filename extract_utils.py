import re


def_strip_re = re.compile(r'^(\w)+ ((?:\w|－)*)')

'''
# 신비:  신비 神秘; ~하다 (스럽다) мистический; таинственный; чудной; чудесный
#  -> 神秘 + ~하다 (스럽다) мистический; таинственный; чудной; чудесный
def strip_definition(word, definition):
    lines = definition.split('\n')
    m = def_strip_re.match(lines)
    if m is not None:
        word_in_def, hanja, stripped_def = m.groups()
        return stripped_def, hanja
    return definition, None
'''


def get_defs(lines):
    word_and_def = lines[0].strip(), lines[1].strip()
    index = 2
    while index < len(lines):
        cur_line = lines[index].strip()
        if len(cur_line) == 0:
            # print(f'{article}\n with empty lines')
            yield word_and_def
            word_and_def = lines[index + 1].strip(), lines[index + 2].strip()
            index += 3
        elif cur_line[0].isdigit():
            word_and_def = word_and_def[0], (word_and_def[1] + ' ' + cur_line)
            index += 1
        else:
            index += 1
    yield word_and_def


def get_hanja(w_and_h):
    ind = w_and_h.find(' ')
    if ind == -1:
        return ''
    else:
        return w_and_h[ind+1:]


def enum_defs(hanja_and_df):
    for index, item in enumerate(hanja_and_df):
        _, df = item
        if len(hanja_and_df) == 1:
            yield df
        else:
            yield f'{index+1}) {df}'


def strip_samples(article):
    article = article.strip()
    lines = article.split('\n')
    assert len(lines) >= 2
    hanja_and_df = list(get_defs(lines))
    return ' '.join(enum_defs(hanja_and_df)), \
           ', '.join(get_hanja(w) for w, df in hanja_and_df)
