import re
import os
import pwd
import grp
import sys
import subprocess
import argparse
import pdb
import tempfile
import logging

import skiplist

class CyrusMigrate(object):
	_cyrusBin = "/usr/lib/cyrus-imapd/"
	_headerMagic = """\241\002\213\015Cyrus mailbox header
"The best thing about this system was that it had lots of goals."
\t--Jim Morris on Andrew
"""
	def __init__(self, imap, oldMailbox, newMailbox, verbose=False):
		self.imap = imap
		self.oldmbox = oldMailbox
		self.newmbox = newMailbox

		if verbose:
			logging.basicConfig(level=logging.DEBUG)
		else:
			logging.basicConfig(level=logging.INFO)

	def __call__(self, reconstruct=False):

		assert self.imap.lm(self.oldmbox), 'Source mailbox %r does not exit' % self.oldmbox

		# Create new mailboxes
		self.createNewMailboxes()

		# Synchronize files from old to new
		self.syncFiles()

		# Reconstruct new mailboxes
		if reconstruct:
			self.reconstruct()

		# Convert folder subscription file
		self.convertSubscription()

		# Convert seen file
		self.convertSeen()

	@staticmethod
	def _mailboxParts(mailbox):
		""" Returns tuple of root mailbox name and domain name.
			Useful if we need to separate the mailbox name from the
			domain name
			Eg:
				user.joe@example.com, returns ('user.joe', 'example.com')
				user.joe, returns ('user.joe', None)
				myShared, returns ('myShared', None)
		"""
		parts = mailbox.split('@')
		return tuple(parts) if len(parts) > 1 else (parts[0], None,)

	def listMailboxes(self, topLevelMailbox):
		""" From the top level mailbox, list all imap folders.
			imap.lm('user.bob.*') will only return subfolders for
			bob, so we have to add the topLevelMailbox into the
			result set. The alternative would be to use imap.lm('user.bob*')
			but this would also return all mailboxes for user.bobby
		"""
		if not self.imap.lm(topLevelMailbox):
			return []
		mailboxes = [topLevelMailbox]

		mailbox, domain = self._mailboxParts(topLevelMailbox)

		for mbox in self.imap.lm('%s.*%s' % (mailbox, ('@' + domain if domain else ''))):
			# Exclude domain mailboxes
			if domain is None and '@' in mbox:
				continue
			mailboxes.append(mbox)
		return mailboxes

	def reconstruct(self):
		""" Reconstructs each new mailbox
		"""
		for mbox in self.listMailboxes(self.newmbox):
			logging.debug('reconstructing %r', mbox)
			self.imap.reconstruct(mbox)

	def oldMailboxNameToNew(self, oldmbox):
		""" Converts old mailbox name to new mailbox.
			The subfolders on the supplied mailbox are extracted
			and inserted into the new mailbox name.

			If the old mailbox is shared, then just return
		"""
		mbox_name,_ = self._mailboxParts(oldmbox)
		oldmbox_name,_ = self._mailboxParts(self.oldmbox)
		newmbox_name, newmbox_domain = self._mailboxParts(self.newmbox)

		# Find subfolders only
		subfolders = mbox_name.replace(oldmbox_name, '', 1)

		# Shared folders have nothing in common, so do prepend new mailbox name
		if not mbox_name.startswith(oldmbox_name):
			newmbox_name = ''

		return newmbox_name + subfolders + ('@' + newmbox_domain if newmbox_domain else '')

	def createNewMailboxes(self):
		""" Creates new mailboxes based on old mailbox tree.
			This is safe to call multiple times as we check
			if the new mailbox exists
		"""
		newMailboxes = self.listMailboxes(self.newmbox)

		for mbox in self.listMailboxes(self.oldmbox):
			newmbox = self.oldMailboxNameToNew(mbox)
			if newmbox not in newMailboxes:
				logging.info('creating mailbox %r', newmbox)
				self.imap.cm(newmbox)
			else:
				logging.debug('mailbox %r exists', newmbox)

	@staticmethod
	def _imapPartitionPath(mbox):
		""" Returns the imap partition file path for the mailbox.
			(see imapd.conf partition-default settings)
			Eg:
				user.bob -> /var/spool/imap/user/bob
				user.bob.folder 1 -> /var/spool/imap/user/bob/folder 1
				user.bob@example.com -> /var/spool/imap/domain/example.com/user/bob
		"""

		name, domain = CyrusMigrate._mailboxParts(mbox)
		if domain:
			return os.path.join('/var/spool/imap/domain', domain, name.replace('.', '/'))
		else:
			return os.path.join('/var/spool/imap', name.replace('.', '/'))

	@staticmethod
	def _imapConfigPath(mbox, suffix):
		""" Returns the full paths to a config file for the given user mailbox.
			(see imapd.conf configdirectory settings).
			Eg:
				'user.bob', '.seen' -> /var/lib/imap/b/bob.seen
				'user.bob@example.net', '.sub' -> /var/lib/imap/domain/e/example.com/user/b/bob.sub
		"""
		assert mbox.startswith('user.')

		mbox_name, domain = CyrusMigrate._mailboxParts(mbox)
		username = mbox_name.split('.')[1]
		if domain: # virtual domain
			path = os.path.join(
				'/var/lib/imap/domain',
				domain[0],
				domain,
				'user',
				username[0]
			)
		else: # local user
			path = os.path.join(
				'/var/lib/imap/user',
				username[0]
			)
		return os.path.join(path, username + suffix)

	def syncFiles(self):
		""" Sync files across from old to new, one directory at a time (non-recursive).
			We use the --delete option to prune deleted files from the destination path
		"""

		for oldmbox in self.listMailboxes(self.oldmbox):
			source = os.path.join(self._imapPartitionPath(oldmbox), '')
			newbmox = self.oldMailboxNameToNew(oldmbox)
			target = self._imapPartitionPath(newbmox)
			logging.debug('Syncing files from %r to %r', source, target)

			# Write the new skiplist file to new location
			stdout = None if logging.getLogger().getEffectiveLevel() == logging.DEBUG else subprocess.PIPE
			subprocess.check_call([
				'rsync',
				'--verbose',
				'--perms',
				'--times',
				'--group',
				'--owner',
				'--dirs',
				'--exclude=cyrus.*',
				'--delete',
				source,
				target
			], stdout=stdout)

	def mailboxIdMap(self):
		mailboxMap = {}
		for oldmbox in self.listMailboxes(self.oldmbox):
			path = self._imapPartitionPath(oldmbox)
			oldmboxId = self._extractMailboxId(path)
			newmbox = self.oldMailboxNameToNew(oldmbox)
			path = self._imapPartitionPath(newmbox)
			newmboxId = self._extractMailboxId(path)
			mailboxMap[oldmboxId] = newmboxId
		return mailboxMap

	def _extractMailboxId(self, path):
		""" Gets the magic mailbox identifier from the cyrus.header file
		"""
		headerFile = os.path.join(path, 'cyrus.header')
		with open(headerFile, 'r') as f:
			assert f.read(len(self._headerMagic)) == self._headerMagic
			line = f.readline()
		return line.split('\t')[1].strip()

	def _chown(self, path, user, group):
		""" Convenience function to change file ownership on a
			file from user/group names.
		"""
		uid = pwd.getpwnam(user).pw_uid
		gid = grp.getgrnam(group).gr_gid

		os.chown(path, uid, gid)

	def _createDirectories(self, toCreate):
		""" Recursively creates missing directories and
			sets ownership to correct user/group
		"""
		path='/'
		for part in [p for p in toCreate.split('/') if p]:
			path = os.path.join(path, part)
			if not os.path.exists(path):
				os.mkdir(path, 0750)
				self._chown(path, 'cyrus', 'mail')

	def convertSeen(self):
		if not self._isUserMigration:
			return

		mailboxIdMap = self.mailboxIdMap()

		oldSeenFile = self._imapConfigPath(self.oldmbox, '.seen')
		newSeenFile = self._imapConfigPath(self.newmbox, '.seen')
		assert os.path.exists(oldSeenFile)

		with open(oldSeenFile, 'rb') as fp:
			header = skiplist.get_header(fp)
			values, keys = skiplist.getkeys(fp)

		try:
			with tempfile.NamedTemporaryFile(delete=False) as tmpFile:
				for v in values:
					tmpFile.file.write('%s\t%s\n' % (mailboxIdMap.get(v, v), keys[v]))

			# Write the new skiplist file to new location
			stdout = None if logging.getLogger().getEffectiveLevel() == logging.DEBUG else subprocess.PIPE
			subprocess.check_call([
				os.path.join(self._cyrusBin, 'cvt_cyrusdb'),
				tmpFile.name,
				'flat',
				newSeenFile,
				'skiplist'
			], stdout=stdout)
			self._chown(newSeenFile, 'cyrus', 'mail')
		finally:
			os.unlink(tmpFile.name)

	@property
	def _isUserMigration(self):
		""" True if target and source are user accounts
		"""
		return self.oldmbox.startswith('user.') and self.newmbox.startswith('user.')

	@staticmethod
	def _mboxFromSubFormat(text):
		""" Subscription files have a odd way of expressing mailbox files.
			For local users, there's no change: user.bob.folder 1 -> user.bob.folder 1
			For virtual domains: user.bob.folder1 @example.com -> example.com!user.bob.folder 1

			Returns the mailbox name for the given line from a subscription .sub file
		"""
		match = re.match(r'^(?:(\S+?)!)?(.*)$', text)
		assert match, 'Failed to parse sub file details %r' % text
		domain, mbox = match.groups()
		return mbox + ('@' + domain if domain else '')

	@staticmethod
	def _mboxToSubFormat(mbox):
		""" Reciprocal to _mboxFromSubFormat. Converts a mailbox name to sub format.
		"""
		mbox_name, domain = CyrusMigrate._mailboxParts(mbox)
		return (domain + '!' if domain else '') + mbox_name

	def convertSubscription(self):
		if not self._isUserMigration:
			return

		oldSubFile = self._imapConfigPath(self.oldmbox, '.sub')
		newSubFile = self._imapConfigPath(self.newmbox, '.sub')

		self._createDirectories(os.path.dirname(newSubFile))

		with open(oldSubFile, 'r') as inFile:
			with open(newSubFile, 'w') as outFile:
				for line in inFile:
					# Ensure the old mailbox exists - ignore if not
					oldmbox = self._mboxFromSubFormat(line.strip('\t\n'))
					if not self.imap.lm(oldmbox):
						logging.warning('Cannot find %r in seen file %r', oldmbox, inFile)
						continue
					newmbox = self.oldMailboxNameToNew(oldmbox)

					# Check this mbox exists (should have been created at start)
					assert self.imap.lm(newmbox), 'Cannot find mailbox %r' % newmbox
					outFile.write('%s\t\n' % self._mboxToSubFormat(newmbox))
		self._chown(newSubFile, 'cyrus', 'mail')


def main():
	import cyruslib
	parser = argparse.ArgumentParser(description='Converts local user imap accounts to domain user accounts')

	parser.add_argument('oldmbox', help='old mailbox name (eg user.bob)')
	parser.add_argument('newmbox', help='new mailbox name (eg user.bob@example.com)')
	parser.add_argument('-r', '--reconstruct', action='store_true', help="reconstruct")
	parser.add_argument('-v', '--verbose', action='store_true', help="verbose")
	args = parser.parse_args()

	imap = cyruslib.CYRUS("imaps://localhost:993")
	imap.login('cyrus', 'password')

	migration = CyrusMigrate(imap, args.oldmbox, args.newmbox, verbose=args.verbose)
	migration(reconstruct=args.reconstruct)

if __name__ == '__main__':
	sys.exit(main())

