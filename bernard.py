#!/usr/bin/env python

import sys
import os
import os.path
import tarfile

def normalize(path):
	"""Return an attempt at avoiding file system quirks."""	
	path = os.path.realpath(path)
	path = os.path.normcase(path)
	path = os.path.normpath(path)
	return path
	
class ConfigFile(object):
	# In these keys, whitespace acts as a list separator
	LISTKEYS = set(['blacklist', 'whitelist'])
	CHAR_COMMENT = '#'

	def __init__(self, cfgfile):
		self.data = {}
		
		# Sane defaults
		self.data['whitelist'] = []
		self.data['blacklist'] = []
		self.data['series'] = []
		self.data['backup'] = []
		self.data['compress'] = []
		
		# Plain key/value parsing
		raw = cfgfile.read()
		for line in raw.split('\n'):
			line = line.strip()
			
			# Break on the first whitespace to find the key/value pair
			kv = line.split(None, 1)

			# Skip comments--comments must only occur at the start of a line!
			if line.startswith(self.CHAR_COMMENT) or len(kv) == 0:
				continue
			
			if kv[0] == 'series':
				self.data['series'] = int(kv[1])
			elif kv[0] == 'compress':
				self.data['compress'] = bool(int(kv[1]))
			elif kv[0] == 'backup':
				self.data[kv[0]].append(normalize(kv[1]))
			elif kv[0] in self.LISTKEYS:
				self.data[kv[0]].extend(kv[1].split())
			
	@property
	def series(self):
		return self.data['series']
	
	@property
	def compress(self):
		return self.data['compress']
	
	@property
	def paths(self):
		return self.data['backup']
		
	@property
	def filter(self):
		"""Return a filter function returning if a path should be backed up."""
		def innerfilter(path):
			ext = os.path.splitext(path)[1]
			
			# We support dealing with extensionless files
			if not ext:
				ext = 'none'
			
			# Whitelist overpowers blacklist
			if not self.data['whitelist']:
				return not ext in self.data['blacklist']
			
			if not self.data['blacklist']:
				return ext in self.data['whitelist']
			
			return ext in self.data['whitelist'] or not ext in self.data['blacklist']
		
		return innerfilter

class Bernard(object):
	def __init__(self, config, name):
		"""Initialize a Bernard driver based on the configuration object."""
		self.config = config
		self.name = name
	
	@property
	def archive_name(self):
		"""Return the name of the backup target."""
		ext = '.tar'
		if self.config.compress:
			ext += '.gz'
		return '{0}-{1}{2}'.format(self.name, self.config.series, ext)
	
	def backup(self):
		"""Back up items on the file system listed in the config object."""
		# Find the modification dates of each backed up file
		archive = tarfile.TarFile(self.archive_name, 'a')
		archive_times = {}
		for info in archive:
			# Leading slashes are removed on Unix
			if not os.path.isabs(info.name):
				file_path = os.path.join('/', info.name)
			file_path = normalize(file_path)
			archive_times[file_path] = int(info.mtime)
		
		# Look at every file we need to have in the archive.
		fs_times = {}
		for path in self.config.paths:
			for entry in os.walk(path):
				for file in entry[2]:
					file = normalize(os.path.join(entry[0], file))
					if self.config.filter(file):
						fs_times[file] = int(os.path.getmtime(file))

		for file in fs_times:
			if not file in archive_times or fs_times[file] > archive_times[file]:
				archive.add(file)

		archive.close()
		
		
if __name__ == '__main__':
	f = open(sys.argv[1], 'r')
	config = ConfigFile(f)
	f.close()
	
	bernard = Bernard(config, os.path.splitext(os.path.basename(sys.argv[1]))[0])
	bernard.backup()
