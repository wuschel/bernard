#!/usr/bin/env python

import unittest
import sys
import os

#os.chdir('tests')

# Grab modules in the root directory
sys.path.insert(0, '../')
import bernard

class SimpleConfigFile(unittest.TestCase):
	def setUp(self):
		f = open('./test.bernard', 'r')
		self.cfg = bernard.ConfigFile(f)
		f.close()

	def test_series(self):
		self.assertEqual(self.cfg.series, 1)
	
	def test_paths(self):
		self.assertEqual(self.cfg.paths, ['/home', '/etc', '/var/test.log'])
	
	def test_filter(self):
		filter = self.cfg.filter
		test_types = {'noextension':False,
			'foo.exe':False, 'example.avi':False,
			'test.txt':True, 'potato.doc':True}
		for type in test_types:
			self.assertEqual(filter(type), test_types[type])

if __name__ == '__main__':
	unittest.main()
