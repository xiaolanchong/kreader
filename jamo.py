# -*- encoding: utf-8 -*-

# http://unicode.org/versions/Unicode5.2.0/ch03.pdf
# 3.12 Hangul Syllable Decomposition
# Jamo codes: http://www.unicode.org/charts/PDF/U1100.pdf

SBase = 0xAC00
LBase = 0x1100
VBase = 0x1161
TBase = 0x11A7
SCount = 11172
LCount = 19
VCount = 21
TCount = 28
NCount = VCount * TCount


def decompose(syllable):
    global SBase, LBase, VBase, TBase, SCount, LCount, VCount, TCount, NCount

    S = ord(syllable)
    SIndex = S - SBase
    L = LBase + SIndex // NCount            #  Leading consonant
    V = VBase + (SIndex % NCount) // TCount #  Vowel
    T = TBase + SIndex % TCount             #  Trailing consonant

    if T == TBase:
        result = (L,V)
    else:
        result = (L,V,T)

    return tuple(map(chr, result))

def compose(L, V, T):
    assert(len(L) == 1)
    assert(len(V) == 1)
    assert(T is None or len(T) == 0 or len(T) == 1)

    global SBase, LBase, VBase, TBase, SCount, LCount, VCount, TCount, NCount

    LIndex = ord(L) - LBase
    VIndex = ord(V) - VBase
    TIndex = 0 if (T is None or len(T) == 0) else (ord(T) - TBase)

    if LIndex < 0 or LIndex >= LCount:
        raise RuntimeError(L + ' is out of range')
    if VIndex < 0 or VIndex >= VCount:
        raise RuntimeError(V + ' is out of range')
    if TIndex < 0 or TIndex >= TCount:
        raise RuntimeError(T + ' is out of range')

    S = (LIndex * VCount + VIndex) * TCount + TIndex + SBase
    return chr(S)

def test_decompose():
    test_values = '항가있닭넓짧'
    for syllable in test_values:
        print(syllable, ':', ''.join(decompose(syllable)))

def test_compose():
    res = compose('ᄒ','ᅡ','ᆼ')
    print('항', res)

    res = compose('ᄀ', 'ᅡ', None)
    print('가', res)

    res = compose('ᄋ', 'ᅵ', 'ᆻ')
    print('있', res)

    res = compose('ᄃ','ᅡ','ᆰ')
    print('닭', res)

    res = compose('ᄂ','ᅥ','ᆲ')
    print('넓', res)

    res = compose('ᄍ','ᅡ','ᆲ')
    print('짧', res)

if __name__ == '__main__':
    test_decompose()
    test_compose()
