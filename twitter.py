# -*- coding: utf-8 -*-

import jamo
import konlpy
from morph_analyzer import Token, MorphAnalyzer

productive_pos = frozenset(['VerbPrefix', 'Verb', 'Determiner', 'NounPrefix', 'Adjective', 'Noun', 'Adverb'])

non_productive_pos = frozenset(['Punctuation', 'Exclamation', 'KoreanParticle', 'Josa', 'Alpha', 'Conjunction', 'Number', 'Foreign'])

ignored_pos = ['Punctuation', 'Alpha', 'Number', 'Foreign']

def is_ignored(pos):
    return pos in ignored_pos

def do_words_suit(a, b):
    if a[0] == b[0]:
        return True

    a_letters = jamo.decompose(a[0])
    b_letters = jamo.decompose(b[0])
    if a_letters[0] == 'ᄋ' and b_letters[0] == 'ᄋ':
        return a_letters[1] == b_letters[1]
    else:
        return a_letters[0] == b_letters[0]

no_stem = ''

# The correct solution is dynamic programming matching
def get_word_to_stem_pairs(words, stems):
    index_stems = 0
    res = []
    for word in words:
        if index_stems < len(stems):
            stem = stems[index_stems]
        else:
            print(index_stems, stems)
            res.append((word, no_stem))
            continue

        if do_words_suit(word, stem):
            res.append((word, stem))
            index_stems += 1
        else:
            res.append((word, no_stem))
    return res

class TwitterAnalyzer(MorphAnalyzer):
    def __init__(self):
        self.parser = konlpy.tag.Twitter()

    def parse(self, text):
        tokens = self.parser.pos(text, norm=False, stem=False)
        stems = self.parser.pos(text, norm=True, stem=True)
        words_to_stems = get_word_to_stem_pairs([word for word, pos in tokens], [word for word, pos in stems])

        out = []
        current_pos = 0
        for index, token in enumerate(tokens):
            word, pos = token[0], token[1]
            if len(word) == 0:
                continue

            skipped_chars = 0
            while text[current_pos][0] != word[0]:
                current_pos += 1
                skipped_chars += 1

            #if skipped_chars:
            #    out.append(Whitespace()) # convert all ws symbols to a space

            dictionary_form = words_to_stems[index][1]
            obj = Token(word=word,
                        dictionary_form=dictionary_form if not is_ignored(pos) else None,
                        pos = pos if pos in non_productive_pos else None
                        )

            current_pos += len(word)
            out.append(obj)
        return out

def test_twitter_output():
    #text = '그는 목이 거의 없을 정도로 살이 뒤룩뒤룩 찐 몸집이 큰 사내로, 코밑에는 커다란 콧수염을 기르고 있었다.'
    text = '4번지에 살고 있는 더즐리 부부'
    text = '그들은 기이하거나 신비스런 일과는 전혀 무관해 보였다.'

    parser = konlpy.tag.Twitter()

    f = parser.pos(text, norm=False, stem=False)
    print(' '.join([word for word, pos in f]))

    s = parser.pos(text, norm=True, stem=True)
    print(' '.join([word + '/' + pos for word, pos in s]))

if __name__ == '__main__':
    test_twitter_output()