# -*- coding: utf-8 -*-

import os.path
import unittest
import sys

sys.path.append(os.path.abspath('..'))
import extract_utils as eu


class TestWordExtraction(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def testSimple(self):
        article = '일과 日課\nрежим дня; ежедневные занятия'
        d, h = eu.strip_samples(article)
        self.assertEqual('日課', h)
        self.assertEqual('режим дня; ежедневные занятия', d)

    def testOnlySamples(self):
        article = '신비 神秘\n~하다 (스럽다) мистический; таинственный; чудной; чудесный'
        d, h = eu.strip_samples(article)
        self.assertEqual('神秘', h)
        self.assertEqual('~하다 (스럽다) мистический; таинственный; чудной; чудесный', d)

    def testMultiple(self):
        article = '제 \nсам\n\n제 制\nсистема\n\n제 祭\nфестиваль; юбилей; годовщина\n\n제 製\nизготовленный; сделанный\n금속~ изготовленный из металла\n\n제 題\nтема; заглавие'
        d, h = eu.strip_samples(article)
        self.assertEqual(', 制, 祭, 製, 題', h)
        self.assertEqual('1) сам 2) система 3) фестиваль; юбилей; годовщина 4) изготовленный; сделанный 5) тема; заглавие', d)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWordExtraction)
    unittest.TextTestRunner(verbosity=2).run(suite)
