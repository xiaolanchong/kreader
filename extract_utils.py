import re


def_strip_re = re.compile('^(\w)+ (\w*); (.+)')
# 신비:  신비 神秘; ~하다 (스럽다) мистический; таинственный; чудной; чудесный
#  -> 神秘 + ~하다 (스럽다) мистический; таинственный; чудной; чудесный
def strip_definition(word, definition):
    m = def_strip_re.match(definition)
    if m is not None:
        word_in_def, hanja, stripped_def = m.groups()
        return stripped_def, hanja
    return definition, None
