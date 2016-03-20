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

         got_title, got_text = ds.get_parsed_text_no_glossary(new_id)
         self.assertEqual(title, got_title)
         self.assertEqual(expected, got_text)

    def testDeletion(self):
        ds, path = self.create_db()
        new_id = ds.add_text(title='Sample title0', source_text='source text0', parsed_text='parsed text0', glossary='')
        self.assertEqual(new_id, 1)
        ds.delete_text(new_id)

        result = ds.get_all_text_descs()
        self.assertEqual(result, [])

    def testPreferences(self):
        ds, path = self.create_db()
        pref = ds.get_preferences()
        self.assertEqual(pref, None)
        ds.set_preferences('{any}')
        pref = ds.get_preferences()
        self.assertEqual(pref, '{any}')

    def testTextUpdate(self):
        ds, path = self.create_db()

        new_id = ds.add_text(title='Sample title0', source_text='source text0',
                             parsed_text='parsed text0', glossary='', total_words=10,
                             unique_words=3)
        self.assertEqual(new_id, 1)

        ds.update_text(text_id=new_id, title='USample title1', source_text='Usource text1',
                              parsed_text='Uparsed text1', glossary='', total_words=100,
                             unique_words=25)

        result = ds.get_all_text_descs()
         #pprint(result)
        self.assertEqual(result, [(1, 'USample title1', 100, 25, 0)])

    def testGetSourceText(self):
        ds, path = self.create_db()
        new_id = ds.add_text(title='Sample title0', source_text='source text0',
                             parsed_text='parsed text0', glossary='', total_words=10,
                             unique_words=3)
        self.assertEqual(new_id, 1)


        result = ds.get_source_text(1)
         #pprint(result)
        self.assertEqual(result, ('Sample title0', 'source text0'))

        self.assertRaises(KeyError, ds.get_source_text, 10)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataStorage)
    unittest.TextTestRunner(verbosity=2).run(suite)