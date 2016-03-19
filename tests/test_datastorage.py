# -*- coding: utf-8 -*-

import os.path
import unittest
import sys
from pprint import pprint

sys.path.append(os.path.abspath('..'))

from datastorage import DataStorage


class TestDataStorage(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.test_number = 0

    def get_db_path(self):
        self.test_number += 1
        return  ':memory:'#'../../_kreader_files/ut_test{0}.db'.format(self.test_number)

    def create_db(self):
        path = self.get_db_path()
        ds = DataStorage(path)
        ds.create_db()
        return ds, path

    def testCreation(self):
        ds, path = self.create_db()
        del ds
#        os.unlink(path)

    def testAddText(self):
        ds, path = self.create_db()
        try:
         new_id = ds.add_text(title='Sample title0', source_text='source text0',
                             parsed_text='parsed text0', glossary='', total_words=10,
                             unique_words=3)
         self.assertEqual(new_id, 1)

         new_id = ds.add_text(title='Sample title1', source_text='source text1',
                              parsed_text='parsed text1', glossary='', total_words=100,
                             unique_words=25)
         self.assertEqual(new_id, 2)

         result = ds.get_all_text_descs()
         #pprint(result)
         self.assertEqual(result, [(1, 'Sample title0', 10, 3, 0), (2, 'Sample title1', 100, 25, 0)])
        finally:
         del ds
         #os.unlink(path)

    def testGetTextById(self):
         expected = 'parsed text0'
         glossary = "{ 'text0' : 1}"
         title = 'Sample title0'
         ds, path = self.create_db()
         new_id = ds.add_text(title=title, source_text='source text0', parsed_text=expected, glossary=glossary)
         got_title, got_text, got_glossary = ds.get_parsed_text(new_id)
         self.assertEqual(title, got_title)
         self.assertEqual(expected, got_text)
         self.assertEqual(glossary, got_glossary)

    def testDeletion(self):
      ds, path = self.create_db()
      new_id = ds.add_text(title='Sample title0', source_text='source text0', parsed_text='parsed text0', glossary='')
      self.assertEqual(new_id, 1)
      ds.delete_text(new_id)

      result = ds.get_all_text_descs()
      self.assertEqual(result, [])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataStorage)
    unittest.TextTestRunner(verbosity=2).run(suite)