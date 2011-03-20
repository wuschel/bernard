#!/usr/bin/env python

__author__ = 'Andrew Aldridge'
__version__ = '0.1-dev'
__license__ = 'BSD'

import datetime
import sys
import os
import os.path
import tarfile

def splitroot(path):
	"""Split the absolute component of the given path."""
	split = os.path.splitdrive(path)
	if not split[0]:
		split = ('/', path.lstrip('/'))
	
	return split

def normalize(path):
	"""Return an attempt at avoiding file system quirks."""	
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
		self.data['series'] = 0
		self.data['backup'] = []
		
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
			elif kv[0] == 'backup':
				self.data[kv[0]].append(normalize(kv[1]))
			elif kv[0] in self.LISTKEYS:
				self.data[kv[0]].extend(kv[1].split())
			
	@property
	def series(self):
		return self.data['series']
	
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
			
			return (ext in self.data['whitelist'] or
				not ext in self.data['blacklist'])
		
		return innerfilter

class Archive(object):
	"""Abstract representation of an underlying archive format."""
	def __init__(self, path):
		self.path = path
		self.archive = None
		self.mtimes = self._list_mtimes()
	
	def _list_mtimes(self):
		"""Return file:modification pairs in the backup file."""
		files = {}

		try:
			archive = tarfile.TarFile(self.path, 'r')
		except IOError:
			return files

		for info in archive:
			file_path = normalize(info.name)
			files[file_path] = int(info.mtime)

		archive.close()
		return files
	
	def add_file(self, fspath):
		"""Return if a file is out-of-date or missing, and add it to the archive
		if necessary."""
		# Cut out the root component of the path to conform with archive paths
		path = normalize(fspath)
		relpath = splitroot(path)[1]
				
		fstime = int(os.path.getmtime(path))
		if not relpath in self.mtimes or fstime > self.mtimes[relpath]:
			# tarfile does not gracefully handle empty archives--only open
			# if we're sure we have files to add.
			if not self.archive:
				self.archive = tarfile.TarFile(self.path, 'a')
			
			self.archive.add(path)
			return True
		return False
	
	def close(self):
		if self.archive:
			self.archive.close()

class Bernard(object):
	def __init__(self, config, name):
		"""Initialize a Bernard driver based on the configuration object."""
		self.config = config
		self.name = name
	
	@property
	def archive_name(self):
		"""Return the name of the backup target."""
		return '{0}-{1}.tar'.format(self.name, self.config.series)

	def backup(self):
		"""Back up items on the file system listed in the config object."""
		archive = Archive(self.archive_name)
		
		try:
			for path in self.config.paths:
				for entry in os.walk(path):
					for filename in entry[2]:
						yield self._backup_file(entry[0], filename, archive)
		finally:
			archive.close()

	def extract(self, revision_n=-1):
		"""Restore the backup file onto the disk."""
		pass

	def _backup_file(self, root, filename, archive):
		"""Return tuple of (path, updated, error)."""
		fpath = normalize(os.path.join(root, filename))
		
		if self.config.filter(fpath):
			is_added = False
			err = False
			try:
				is_added = archive.add_file(fpath)
			except EnvironmentError:
				err = True
			
			return (fpath, is_added, err)

class BernardArgs(object):
	ACTION_BACKUP = 'b'
	ACTION_RESTORE = 'r'
	ACTION_HELP = 'h'
	ACTIONS = set([ACTION_BACKUP, ACTION_RESTORE, ACTION_HELP])

	HELP = '''
Bernard {0} Copyright {1} {2}
Usage:
    bernard.py [ACTION] [BACKUP]
ACTION may be one of:
    b    Backup
    r    Restore
    h    Help (show this help page)
BACKUP must be the name of a backup to create, and there must be a file
./[BACKUP].bernard.'''.format(__version__,
                              datetime.date.today().year,
                              __author__)

	@classmethod
	def show_help(cls, status):
		print(cls.HELP)
		exit(status)

	def __init__(self, args):
		self.action = ''
		self.backup_name = ''
		
		# Check for illegal or insufficient arguments
		if (len(args) < 3 or
			not args[1] in self.ACTIONS):
			self.show_help(1)

		self.action = args[1]
		self.backup_name = args[2]

		if self.action == self.ACTION_HELP:
			self.show_help(0)
	
	@property
	def should_backup(self):
		return self.action == self.ACTION_BACKUP
	
	@property
	def should_restore(self):
		return self.action == self.ACTION_RESTORE

	@property
	def config_path(self):
		return self.backup_name + '.bernard'

if __name__ == '__main__':
	args = BernardArgs(sys.argv)
	f = open(args.config_path, 'r')
	config = ConfigFile(f)
	f.close()
	
	bernard = Bernard(config, args.backup_name)
	if args.should_backup:
		for path,updated,err in bernard.backup():
			if err:
				sys.stderr.write('e')
			elif updated:
				sys.stderr.write('u')
			else:
				sys.stderr.write('-')
			sys.stderr.flush()
	if args.should_restore:
		bernard.restore()
