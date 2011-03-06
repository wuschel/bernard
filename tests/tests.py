#!/usr/bin/env python

import unittest
import sys
import bernard

# Grab modules in the root directory
sys.path.insert(0, '.')

class SimpleConfigFile(unittest.TestCase):
	def setUp(self):
		f = open('./test.bernard', 'r')
		self.cfg = bernard.ConfigFile(f)
		f.close()

	def test_series(self):
		self.assertEqual(self.cfg.series, 1)
	
	def test_paths(self):
		self.assertEqual(self.cfg.paths, ['/home', '/etc', '/var/test.log'])
	
	def test_compress(self):
		self.assertEqual(self.cfg.compress, False)
	
	def test_filter(self):
		filter = self.cfg.filter
		test_types = {'noextension':False,
			'foo.exe':False, 'example.avi':False,
			'test.txt':True, 'potato.doc':True}
		for type in test_types:
			self.assertEqual(filter(type), test_types[type])

class BernardTest(unittest.TestCase):
	def setUp(self):
		f = open('./test2.bernard', 'r')
		cfg = bernard.ConfigFile(f)
		f.close()
		self.bernard = bernard.Bernard(cfg, 'test2')
	
	def test_compressedArchiveName(self):
		self.assertEqual(self.bernard.archive_name, 'test2-3.tar.gz')

	def test_uncompressedArchiveName(self):
		f = open('./testuncompressed.bernard', 'r')
		cfg = bernard.ConfigFile(f)
		f.close()
		backup = bernard.Bernard(cfg, 'testuncompressed')
	
		self.assertEqual(backup.archive_name, 'testuncompressed-1.tar')
	
	
if __name__ == '__main__':
	unittest.main()
