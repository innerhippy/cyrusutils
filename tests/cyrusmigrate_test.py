""" Unit tests for CyrusMigrate class
"""
import unittest
from cyrusutils.cyrusmigrate import CyrusMigrate

class MockImap(object):
	def __init__(self):
		super(MockImap, self).__init__()
		self._mailboxes = {
			'user.bob': [
				'user.bob',
			],
			'user.bob.*': [
				'user.bob.ufolder1',
				'user.bob.ufolder1.sub1',
				'user.bob.ufolder1.sub 2',
				'user.bob.ufolder 2',
				'user.bob.ufolder 2.sub1',
				'user.bob.ufolder 2.sub 2',
				'user.bob.vfolder1@example.com',
				'user.bob.vfolder1.sub1@example.com',
				'user.bob.vfolder1.sub 2@example.com',
				'user.bob.vfolder 2@example.com',
				'user.bob.vfolder 2.sub1@example.com',
				'user.bob.vfolder 2.sub 2@example.com',
			],
			'user.joe@example.com': [
				'user.joe@example.com',
			],
			'user.joe.*@example.com': [
				'user.joe.vfolder1@example.com',
				'user.joe.vfolder1.sub1@example.com',
				'user.joe.vfolder1.sub 2@example.com',
				'user.joe.vfolder 2@example.com',
				'user.joe.vfolder 2.sub1@example.com',
				'user.joe.vfolder 2.sub 2@example.com',
			],
			'shared': [
				'shared'
			],
			'shared.*': [
				'shared.folder1',
				'shared.folder1.sub',
				'shared.folder 2',
				'shared.folder 2.sub',
			],
			'shared@example.com': [
				'shared@example.com'
			],
			'shared.*@example.com': [
				'shared.folder1@example.com',
				'shared.folder1.sub@example.com',
				'shared.folder 2@example.com',
				'shared.folder 2.sub@example.com',
			],
		}

	def lm(self, mailbox):
		return self._mailboxes.get(mailbox, [])

	def reconstruct(self, mailbox):
		pass

	def cm(self, mailbox):
		pass

class Test_CyrusMigrate_Common(unittest.TestCase):
	""" Test cyrusmigrate common functions (static or class)
	"""
	def test_mailboxParts(self):
		self.assertEqual(
			CyrusMigrate._mailboxParts('user.bob'), 
			('user.bob', None)
		)
		self.assertEqual(
			CyrusMigrate._mailboxParts('user.bob.myMail'), 
			('user.bob.myMail', None)
		)
		self.assertEqual(
			CyrusMigrate._mailboxParts('user.bob.sub 1'), 
			('user.bob.sub 1', None)
		)
		self.assertEqual(
			CyrusMigrate._mailboxParts('user.bob@example.com'), 
			('user.bob', 'example.com')
		)
		self.assertEqual(
			CyrusMigrate._mailboxParts('user.bob.myMail@example.com'), 
			('user.bob.myMail', 'example.com')
		)
		self.assertEqual(
			CyrusMigrate._mailboxParts('user.bob.sub 1@example.com'), 
			('user.bob.sub 1', 'example.com')
		)

	def test_mboxFromSubFormat(self):
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('user.bob'), 
			'user.bob'
		)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('user.bob.folder1'), 
			'user.bob.folder1'
		)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('user.bob.folder 2'), 
			'user.bob.folder 2'
		)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('shared'), 
			'shared'
		)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('shared.sub1'), 
			'shared.sub1'
		)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('shared.sub 2'), 
			'shared.sub 2'
		)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('example.com!user.bob.folder1'), 
			'user.bob.folder1@example.com'
		)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('example.com!user.bob.folder 2'), 
			'user.bob.folder 2@example.com'
		)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('example.com!user.bob'), 
			'user.bob@example.com'
			)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('example.com!user.bob'), 
			'user.bob@example.com'
			)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('example.com!shared'), 
			'shared@example.com'
			)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('example.com!shared.sub1'), 
			'shared.sub1@example.com'
			)
		self.assertEqual(
			CyrusMigrate._mboxFromSubFormat('example.com!shared.sub 2'), 
			'shared.sub 2@example.com'
			)

	def test_mboxToSubFormat(self):
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('user.bob'), 
			'user.bob'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('user.bob.folder1'), 
			'user.bob.folder1'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('user.bob.folder 2'), 
			'user.bob.folder 2'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('shared'), 
			'shared'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('shared.sub1'), 
			'shared.sub1'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('shared.sub 2'), 
			'shared.sub 2'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('user.bob@example.com'), 
			'example.com!user.bob'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('user.bob.folder1@example.com'), 
			'example.com!user.bob.folder1'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('user.bob.folder 2@example.com'), 
			'example.com!user.bob.folder 2'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('shared@example.com'), 
			'example.com!shared'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('shared.sub1@example.com'), 
			'example.com!shared.sub1'
			)
		self.assertEqual(
			CyrusMigrate._mboxToSubFormat('shared.sub 2@example.com'), 
			'example.com!shared.sub 2'
			)


class Test_CyrusMigrate_User_LocalToLocal(unittest.TestCase):
	""" Test cyrusmigrate for local user to local user
	"""
	def setUp(self):
		imap = MockImap()
		self.cyrus = CyrusMigrate(imap, 'user.bob', 'user.joe')

	def test_oldMailboxes(self):
		self.assertEqual(
			self.cyrus.oldMailboxes,
			[
				'user.bob',
				'user.bob.ufolder1',
				'user.bob.ufolder1.sub1',
				'user.bob.ufolder1.sub 2',
				'user.bob.ufolder 2',
				'user.bob.ufolder 2.sub1',
				'user.bob.ufolder 2.sub 2',
			]
		)

	def test_newMailboxes(self):
		self.assertEqual(self.cyrus.newMailboxes, [])

	def test_oldMailboxNameToNew(self):
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.bob'), 
			'user.joe'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.bob.folder1'), 
			'user.joe.folder1'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.bob.folder 2'), 
			'user.joe.folder 2'
		)

	def test_oldImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.bob'), 
			'/var/spool/imap/user/bob'
		)
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.bob.folder 1'), 
			'/var/spool/imap/user/bob/folder 1'
		)
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.bob.folder 1.sub'), 
			'/var/spool/imap/user/bob/folder 1/sub'
		)

	def test_newImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.joe'), 
			'/var/spool/imap/user/joe'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.joe.folder 1'), 
			'/var/spool/imap/user/joe/folder 1'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.joe.folder 1.sub'), 
			'/var/spool/imap/user/joe/folder 1/sub'
		)

	def test_oldImapConfigPath(self):
		self.assertEqual(
			self.cyrus.oldImapConfigPath('.seen'), 
			'/var/lib/imap/user/b/bob.seen'
		)

	def test_newImapConfigPath(self):
		self.assertEqual(
			self.cyrus.newImapConfigPath('.seen'), 
			'/var/lib/imap/user/j/joe.seen'
		)

	def test_isUserMigration(self):
		self.assertEqual(self.cyrus._isUserMigration, True)


class Test_CyrusMigrate_User_LocalToVirtual(unittest.TestCase):
	""" Test cyrusmigrate for local user to virtual user
	"""
	def setUp(self):
		imap = MockImap()
		self.cyrus = CyrusMigrate(imap, 'user.bob', 'user.brian@example.com')

	def test_oldMailboxes(self):
		self.assertEqual(
			self.cyrus.oldMailboxes,
			[
				'user.bob',
				'user.bob.ufolder1',
				'user.bob.ufolder1.sub1',
				'user.bob.ufolder1.sub 2',
				'user.bob.ufolder 2',
				'user.bob.ufolder 2.sub1',
				'user.bob.ufolder 2.sub 2',
			]
		)

	def test_newMailboxes(self):
		self.assertEqual(self.cyrus.newMailboxes, [])

	def test_oldMailboxNameToNew(self):
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.bob'), 
			'user.brian@example.com'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.bob.folder1'), 
			'user.brian.folder1@example.com'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.bob.folder 2'), 
			'user.brian.folder 2@example.com'
		)

	def test_oldImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.bob'), 
			'/var/spool/imap/user/bob')
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.bob.folder 1'), 
			'/var/spool/imap/user/bob/folder 1')
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.bob.folder 1.sub'), 
			'/var/spool/imap/user/bob/folder 1/sub')

	def test_newImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.brian@example.com'), 
			'/var/spool/imap/domain/example.com/user/brian'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.brian.folder 1@example.com'), 
			'/var/spool/imap/domain/example.com/user/brian/folder 1'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.brian.folder 1.sub@example.com'), 
			'/var/spool/imap/domain/example.com/user/brian/folder 1/sub'
		)

	def test_oldImapConfigPath(self):
		self.assertEqual(
			self.cyrus.oldImapConfigPath('.seen'), 
			'/var/lib/imap/user/b/bob.seen'
		)

	def test_newImapConfigPath(self):
		self.assertEqual(
			self.cyrus.newImapConfigPath('.seen'), 
			'/var/lib/imap/domain/e/example.com/user/b/brian.seen')

	def test_isUserMigration(self):
		self.assertEqual(self.cyrus._isUserMigration, True)


class Test_CyrusMigrate_User_VirtualToLocal(unittest.TestCase):
	""" Test cyrusmigrate for local user to virtual user
	"""
	def setUp(self):
		imap = MockImap()
		self.cyrus = CyrusMigrate(imap, 'user.joe@example.com', 'user.brian')

	def test_oldMailboxes(self):
		self.assertEqual(
			self.cyrus.oldMailboxes,
			[
				'user.joe@example.com',
				'user.joe.vfolder1@example.com',
				'user.joe.vfolder1.sub1@example.com',
				'user.joe.vfolder1.sub 2@example.com',
				'user.joe.vfolder 2@example.com',
				'user.joe.vfolder 2.sub1@example.com',
				'user.joe.vfolder 2.sub 2@example.com',
			]
		)

	def test_newMailboxes(self):
		self.assertEqual(self.cyrus.newMailboxes, [])

	def test_oldMailboxNameToNew(self):
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.joe@example.com'), 
			'user.brian'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.joe.folder1@example.com'), 
			'user.brian.folder1'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.joe.folder 2@example.com'), 
			'user.brian.folder 2'
		)

	def test_oldImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.joe@example.com'), 
			'/var/spool/imap/domain/example.com/user/joe'
		)
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.joe.folder 1@example.com'), 
			'/var/spool/imap/domain/example.com/user/joe/folder 1')
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.joe.folder 1.sub@example.com'), 
			'/var/spool/imap/domain/example.com/user/joe/folder 1/sub')

	def test_newImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.brian'), 
			'/var/spool/imap/user/brian'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.brian.folder 1'), 
			'/var/spool/imap/user/brian/folder 1'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.brian.folder 1.sub'), 
			'/var/spool/imap/user/brian/folder 1/sub'
		)

	def test_oldImapConfigPath(self):
		self.assertEqual(
			self.cyrus.oldImapConfigPath('.seen'), 
			'/var/lib/imap/domain/e/example.com/user/j/joe.seen'
			)

	def test_newImapConfigPath(self):
		self.assertEqual(
			self.cyrus.newImapConfigPath('.seen'), 
			'/var/lib/imap/user/b/brian.seen')

	def test_isUserMigration(self):
		self.assertEqual(self.cyrus._isUserMigration, True)

class Test_CyrusMigrate_User_VirtualToVirtual(unittest.TestCase):
	""" Test cyrusmigrate for local user to virtual user
	"""
	def setUp(self):
		imap = MockImap()
		self.cyrus = CyrusMigrate(imap, 'user.joe@example.com', 'user.brian@another.com')

	def test_oldMailboxes(self):
		self.assertEqual(
			self.cyrus.oldMailboxes,
			[
				'user.joe@example.com',
				'user.joe.vfolder1@example.com',
				'user.joe.vfolder1.sub1@example.com',
				'user.joe.vfolder1.sub 2@example.com',
				'user.joe.vfolder 2@example.com',
				'user.joe.vfolder 2.sub1@example.com',
				'user.joe.vfolder 2.sub 2@example.com',
			]
		)

	def test_newMailboxes(self):
		self.assertEqual(self.cyrus.newMailboxes, [])

	def test_oldMailboxNameToNew(self):
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.joe@example.com'), 
			'user.brian@another.com'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.joe.folder1@example.com'), 
			'user.brian.folder1@another.com'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('user.joe.folder 2@example.com'), 
			'user.brian.folder 2@another.com'
		)

	def test_oldImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.joe@example.com'), 
			'/var/spool/imap/domain/example.com/user/joe'
		)
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.joe.folder 1@example.com'), 
			'/var/spool/imap/domain/example.com/user/joe/folder 1')
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('user.joe.folder 1.sub@example.com'), 
			'/var/spool/imap/domain/example.com/user/joe/folder 1/sub')

	def test_newImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.brian@another.com'), 
			'/var/spool/imap/domain/another.com/user/brian'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.brian.folder 1@another.com'), 
			'/var/spool/imap/domain/another.com/user/brian/folder 1'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('user.brian.folder 1.sub@another.com'), 
			'/var/spool/imap/domain/another.com/user/brian/folder 1/sub'
		)

	def test_oldImapConfigPath(self):
		self.assertEqual(
			self.cyrus.oldImapConfigPath('.seen'), 
			'/var/lib/imap/domain/e/example.com/user/j/joe.seen'
			)

	def test_newImapConfigPath(self):
		self.assertEqual(
			self.cyrus.newImapConfigPath('.seen'), 
			'/var/lib/imap/domain/a/another.com/user/b/brian.seen')

	def test_isUserMigration(self):
		self.assertEqual(self.cyrus._isUserMigration, True)


class Test_CyrusMigrate_Shared_LocalToLocal(unittest.TestCase):
	""" Test cyrusmigrate for shared local to shared local
	"""
	def setUp(self):
		imap = MockImap()
		self.cyrus = CyrusMigrate(imap, 'shared', 'another')

	def test_oldMailboxes(self):
		self.assertEqual(
			self.cyrus.oldMailboxes,
			[
				'shared',
				'shared.folder1',
				'shared.folder1.sub',
				'shared.folder 2',
				'shared.folder 2.sub',
			]
		)

	def test_newMailboxes(self):
		self.assertEqual(self.cyrus.newMailboxes, [])

	def test_oldMailboxNameToNew(self):
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('shared'), 
			'another'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('shared.folder1'), 
			'another.folder1'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('shared.folder1.sub'), 
			'another.folder1.sub'
		)

	def test_oldImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('shared'), 
			'/var/spool/imap/shared'
		)
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('shared.folder1'), 
			'/var/spool/imap/shared/folder1')
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('shared.folder 2.sub'), 
			'/var/spool/imap/shared/folder 2/sub')

	def test_newImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.newImapPartitionPath('another'), 
			'/var/spool/imap/another'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('another.folder 1'), 
			'/var/spool/imap/another/folder 1'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('another.folder 2.sub'), 
			'/var/spool/imap/another/folder 2/sub'
		)

	def test_oldImapConfigPath(self):
		""" Shared folders cannot have .seen files (or .sub files)
		"""
		self.assertRaises(Exception, self.cyrus.oldImapConfigPath, '.seen')

	def test_newImapConfigPath(self):
		""" Shared folders cannot have .seen files
		"""
		self.assertRaises(Exception, self.cyrus.newImapConfigPath, '.seen')

	def test_isUserMigration(self):
		""" No it ain't
		"""
		self.assertEqual(self.cyrus._isUserMigration, False)

class Test_CyrusMigrate_Shared_LocalToVirtual(unittest.TestCase):
	""" Test cyrusmigrate for shared local to shared virtual
	"""
	def setUp(self):
		imap = MockImap()
		self.cyrus = CyrusMigrate(imap, 'shared', 'another@hosting.com')

	def test_oldMailboxes(self):
		self.assertEqual(
			self.cyrus.oldMailboxes,
			[
				'shared',
				'shared.folder1',
				'shared.folder1.sub',
				'shared.folder 2',
				'shared.folder 2.sub',
			]
		)

	def test_newMailboxes(self):
		self.assertEqual(self.cyrus.newMailboxes, [])

	def test_oldMailboxNameToNew(self):
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('shared'), 
			'another@hosting.com'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('shared.folder1'), 
			'another.folder1@hosting.com'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('shared.folder1.sub'), 
			'another.folder1.sub@hosting.com'
		)

	def test_oldImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('shared'), 
			'/var/spool/imap/shared'
		)
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('shared.folder1'), 
			'/var/spool/imap/shared/folder1')
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('shared.folder 2.sub'), 
			'/var/spool/imap/shared/folder 2/sub')

	def test_newImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.newImapPartitionPath('another@hosting.com'), 
			'/var/spool/imap/domain/hosting.com/another'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('another.folder 1@hosting.com'), 
			'/var/spool/imap/domain/hosting.com/another/folder 1'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('another.folder 2.sub@hosting.com'), 
			'/var/spool/imap/domain/hosting.com/another/folder 2/sub'
		)

	def test_oldImapConfigPath(self):
		""" Shared folders cannot have .seen files (or .sub files)
		"""
		self.assertRaises(Exception, self.cyrus.oldImapConfigPath, '.seen')

	def test_newImapConfigPath(self):
		""" Shared folders cannot have .seen files
		"""
		self.assertRaises(Exception, self.cyrus.newImapConfigPath, '.seen')

	def test_isUserMigration(self):
		""" No it ain't
		"""
		self.assertEqual(self.cyrus._isUserMigration, False)

class Test_CyrusMigrate_Shared_VirtualToVirtual(unittest.TestCase):
	""" Test cyrusmigrate for shared virtual to virtual
	"""
	def setUp(self):
		imap = MockImap()
		self.cyrus = CyrusMigrate(imap, 'shared@example.com', 'another@hosting.com')

	def test_oldMailboxes(self):
		self.assertEqual(
			self.cyrus.oldMailboxes,
			[
				'shared@example.com',
				'shared.folder1@example.com',
				'shared.folder1.sub@example.com',
				'shared.folder 2@example.com',
				'shared.folder 2.sub@example.com',
			]
		)

	def test_newMailboxes(self):
		self.assertEqual(self.cyrus.newMailboxes, [])

	def test_oldMailboxNameToNew(self):
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('shared@example.com'), 
			'another@hosting.com'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('shared.folder1@example.com'), 
			'another.folder1@hosting.com'
		)
		self.assertEqual(
			self.cyrus.oldMailboxNameToNew('shared.folder1.sub@example.com'), 
			'another.folder1.sub@hosting.com'
		)

	def test_oldImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('shared@example.com'), 
			'/var/spool/imap/domain/example.com/shared'
		)
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('shared.folder1@example.com'), 
			'/var/spool/imap/domain/example.com/shared/folder1')
		self.assertEqual(
			self.cyrus.oldImapPartitionPath('shared.folder 2.sub@example.com'), 
			'/var/spool/imap/domain/example.com/shared/folder 2/sub')

	def test_newImapPartitionPath(self):
		self.assertEqual(
			self.cyrus.newImapPartitionPath('another@hosting.com'), 
			'/var/spool/imap/domain/hosting.com/another'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('another.folder 1@hosting.com'), 
			'/var/spool/imap/domain/hosting.com/another/folder 1'
		)
		self.assertEqual(
			self.cyrus.newImapPartitionPath('another.folder 2.sub@hosting.com'), 
			'/var/spool/imap/domain/hosting.com/another/folder 2/sub'
		)

	def test_oldImapConfigPath(self):
		""" Shared folders cannot have .seen files (or .sub files)
		"""
		self.assertRaises(Exception, self.cyrus.oldImapConfigPath, '.seen')

	def test_newImapConfigPath(self):
		""" Shared folders cannot have .seen files
		"""
		self.assertRaises(Exception, self.cyrus.newImapConfigPath, '.seen')

	def test_isUserMigration(self):
		""" No it ain't
		"""
		self.assertEqual(self.cyrus._isUserMigration, False)
