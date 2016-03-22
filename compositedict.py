# -*- coding: utf-8 -*-

from ezsajeon import EzSajeon
from stardictsajeon import StardictRuSajeon
from stardictsajeon import StardictEnSajeon

class CompositeDictionary:
   def __init__(self, extra_dict):
      self.ezsajeon = EzSajeon()
      self.stardict_ru = StardictRuSajeon() if extra_dict else None
      self.stardict_en = StardictEnSajeon() if extra_dict else None

   def get_definition(self, word, add_samples=False):
      main_article = self.ezsajeon.get_definition(word)

      if self.stardict_ru:
        aux_article = self.stardict_ru.get_definition(word, add_samples)
        main_article += '\n'
        main_article += aux_article

      if self.stardict_en:
        aux_article = self.stardict_en.get_definition(word, add_samples)
        #if aux_article:
        if main_article[-1] != '\n':
            main_article += '\n'
        main_article += aux_article
      return main_article


if __name__ == "__main__":
    dc = CompositeDictionary(True)
    res = dc.get_definition('콧수염')
    print(res)

    print('-' * 25)
    res = dc.get_definition('콧수염', True)
    print(res)