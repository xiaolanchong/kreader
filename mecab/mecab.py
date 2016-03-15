# -*- coding: utf-8 -*-

import os.path
import ctypes

def is_windows():
    from sys import platform as _platform
    return _platform == "win32"

class Mecab:
    def __init__(self):
        this_dir = os.path.dirname(__file__)

        if is_windows():
            dll_path = os.path.join(this_dir, 'libmecab.dll')
        else:
            dll_path = os.path.join(this_dir, 'libmecab.so')

        dict_dir = os.path.join(this_dir, 'mecabrc')
        rcfile_path = os.path.join(dict_dir, 'dicrc')

        self.mecab_dll = ctypes.cdll.LoadLibrary(dll_path)

        mecab_new2_p = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_char_p)
        self.mecab_new2 = mecab_new2_p(('mecab_new2', self.mecab_dll))

        mecab_destroy_p = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
        self.mecab_destroy = mecab_destroy_p(('mecab_destroy', self.mecab_dll))

        mecab_sparse_tostr_p = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_void_p, ctypes.c_char_p)
        self.mecab_sparse_tostr = mecab_sparse_tostr_p(('mecab_sparse_tostr', self.mecab_dll))

        mecab_strerror_p = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_void_p)
        self.mecab_strerror = mecab_strerror_p(('mecab_strerror', self.mecab_dll))

        # m     word
        # f[0]  overall part of speech
        # f[1]  extra info on PoS?
        # f[2]  F/T
        # f[3]  word
        # f[4]  Inflect
        # f[5]  initial PoS
        # f[6]  final PoS
        # f[7]  decomposed elements: 보였 -> 보이/VV/*+었/EP/*
        in_arg = '--rcfile={0} --dicdir={1} --node-format={2}'.format(rcfile_path, dict_dir, '%m\\t%f[0]\\t%f[7]\\n')
        self.engine = self.mecab_new2(in_arg.encode())

        if self.engine is None:
            raise RuntimeError('Mecab engine init failed')

    def parse(self, text):
        """
        Parses the given text and returns list of tuples (word, dictionary/non-inflected form, overall PoS),
        PoS may be complex, e.g. VV+EP.
        Raises RuntimeError in case of error

        text -- text to split into tokens
        """
        res = self.mecab_sparse_tostr(self.engine, text.encode())
        if res is None:
            err_desc = self.mecab_strerror(self.engine)
            raise RuntimeError(err_desc.decode('utf-8'))
        res = res.decode('utf-8')
        return self.post_process(res)

    def get_dictionary_form(self, word, pos, composition):
        if composition is not None and len(composition):
            elements = composition.split('+')
            if len(elements) == 0:
                raise RuntimeError('Word decomposition is ill-formatted: {0}'.format(composition))
            stem, stem_pos, _ =  elements[0].split('/')
            #print(stem_pos)
            #assert(stem_pos[0] == 'V' or stem_pos[0] == 'X')  # verb/auxiliarys are conjugated
            # TODO: why patched in mecab_analyzer?
            return stem# + '다'
        else:
            return word

    def post_process(self, text_out):
        out = []
        for line in text_out.split('\n'):
            if line != 'EOS':
                word, pos, composition = line.split('\t')
                dictionary_form = self.get_dictionary_form(word, pos, composition)

                #print(word, pos, decomposed_parts)
                out.append((word, dictionary_form, pos))
            else:
                break
        return out

    def __del__(self):
        if self.engine is not None:
            self.mecab_destroy(self.engine)

def test_output():
    mecab = Mecab()
    text = '프리벳가 4번지에 살고 있는 더즐리 부부는 보였다'
    res = mecab.parse(text)
    print(res)

if __name__ == '__main__':
    test_output()
