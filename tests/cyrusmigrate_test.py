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
			'user.bob@example.com': [
				'user.bob@example.com',
			],
			'user.bob.*@example.com': [
				'user.bob.vfolder1@example.com',
				'user.bob.vfolder1.sub1@example.com',
				'user.bob.vfolder1.sub 2@example.com',
				'user.bob.vfolder 2@example.com',
				'user.bob.vfolder 2.sub1@example.com',
				'user.bob.vfolder 2.sub 2@example.com',
			],
			'user.joe': [
				'user.joe',
			],
			'user.joe.*': [
				'user.joe.ufolder1',
				'user.joe.ufolder1.sub1',
				'user.joe.ufolder1.sub 2',
				'user.joe.ufolder 2',
				'user.joe.ufolder 2.sub1',
				'user.joe.ufolder 2.sub 2',
				'user.joe.vfolder1@example.com',
				'user.joe.vfolder1.sub1@example.com',
				'user.joe.vfolder1.sub 2@example.com',
				'user.joe.vfolder 2@example.com',
				'user.joe.vfolder 2.sub1@example.com',
				'user.joe.vfolder 2.sub 2@example.com',
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
		}

	def lm(self, mailbox):
		return self._mailboxes.get(mailbox, [])

	def reconstruct(self, mailbox):
		pass

	def cm(self, mailbox):
		pass

class Test_CyrusMigrate_LocalToLocal(unittest.TestCase):
	""" Test basic SignalRecorder class
	"""
	def setUp(self):
		imap = MockImap()
		self.cyrus = CyrusMigrate(imap, 'user.bob', 'user.joe')

	def test_mailboxParts(self):
		self.assertEqual(CyrusMigrate._mailboxParts('user.bob'), ('user.bob', None))
		self.assertEqual(CyrusMigrate._mailboxParts('user.bob.myMail'), ('user.bob.myMail', None))

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
		self.assertEqual(
			self.cyrus.newMailboxes,
			[
				'user.joe',
				'user.joe.ufolder1',
				'user.joe.ufolder1.sub1',
				'user.joe.ufolder1.sub 2',
				'user.joe.ufolder 2',
				'user.joe.ufolder 2.sub1',
				'user.joe.ufolder 2.sub 2',
			]
		)

	def test_oldMailboxNameToNew(self):
		self.assertEqual(self.cyrus.oldMailboxNameToNew('user.bob'), 'user.joe')
		self.assertEqual(self.cyrus.oldMailboxNameToNew('user.bob.folder1'), 'user.joe.folder1')
		self.assertEqual(self.cyrus.oldMailboxNameToNew('user.bob.folder 2'), 'user.joe.folder 2')

	def test_oldImapPartitionPath(self):
		self.assertEqual(self.cyrus.oldImapPartitionPath('user.bob'), '/var/spool/imap/user/bob')
		self.assertEqual(self.cyrus.oldImapPartitionPath('user.bob.folder 1'), '/var/spool/imap/user/bob/folder 1')
		self.assertEqual(self.cyrus.oldImapPartitionPath('user.bob.folder 1.sub'), '/var/spool/imap/user/bob/folder 1/sub')

	def test_newImapPartitionPath(self):
		self.assertEqual(self.cyrus.newImapPartitionPath('user.joe'), '/var/spool/imap/user/joe')
		self.assertEqual(self.cyrus.newImapPartitionPath('user.joe.folder 1'), '/var/spool/imap/user/joe/folder 1')
		self.assertEqual(self.cyrus.newImapPartitionPath('user.joe.folder 1.sub'), '/var/spool/imap/user/joe/folder 1/sub')

	def test_oldImapConfigPath(self):
		self.assertEqual(self.cyrus.oldImapConfigPath('.seen'), '/var/lib/imap/user/b/bob.seen')

	def test_newImapConfigPath(self):
		self.assertEqual(self.cyrus.newImapConfigPath('.seen'), '/var/lib/imap/user/j/joe.seen')

	def test_isUserMigration(self):
		self.assertEqual(self.cyrus._isUserMigration, True)

	def test__mboxFromSubFormat(self):
		self.assertEqual(self.cyrus._mboxFromSubFormat('user.bob'), 'user.bob')
		self.assertEqual(self.cyrus._mboxFromSubFormat('user.bob.folder1'), 'user.bob.folder1')
		self.assertEqual(self.cyrus._mboxFromSubFormat('user.bob.folder 2'), 'user.bob.folder 2')

	def test__mboxToSubFormat(self):
		self.assertEqual(self.cyrus._mboxToSubFormat('user.bob'), 'user.bob')
		self.assertEqual(self.cyrus._mboxToSubFormat('user.bob.folder1'), 'user.bob.folder1')
		self.assertEqual(self.cyrus._mboxToSubFormat('user.bob.folder 2'), 'user.bob.folder 2')


class Test_CyrusMigrateLocal(unittest.TestCase):
	""" Test basic SignalRecorder class
	"""
#	def test_mailboxParts_userLocal(self):
#		self.assertEqual(CyrusMigrate._mailboxParts('user.joe'), ('user.joe', None))
#		self.assertEqual(CyrusMigrate._mailboxParts('user.joe.myMail'), ('user.joe.myMail', None))
#
#	def test_mailboxParts_userVirtual(self):
#		self.assertEqual(CyrusMigrate._mailboxParts('user.joe@example.com'), ('user.joe', 'example.com'))
#		self.assertEqual(CyrusMigrate._mailboxParts('user.joe.myMail@example.com'), ('user.joe.myMail', 'example.com'))
#
#	def test_mailboxParts_sharedLocal(self):
#		self.assertEqual(CyrusMigrate._mailboxParts('sharedMbox'), ('sharedMbox', None))
#		self.assertEqual(CyrusMigrate._mailboxParts('sharedMbox.another'), ('sharedMbox.another', None))
#
#	def test_mailboxParts_sharedVirtual(self):
#		self.assertEqual(CyrusMigrate._mailboxParts('sharedMbox@example.com'), ('sharedMbox', 'example.com'))
#		self.assertEqual(CyrusMigrate._mailboxParts('sharedMbox.another@example.com'), ('sharedMbox.another', 'example.com'))
#
#	def test_oldMailboxes(self):
#		imap = MockImap()
#		cyrus = CyrusMigrate(imap, 'user.bob', None)
#		self.assertEqual(
#				cyrus.oldMailboxes,
#			[
#				'user.bob',
#				'user.bob.ufolder1',
#				'user.bob.ufolder1.sub1',
#				'user.bob.ufolder1.sub 2',
#				'user.bob.ufolder 2',
#				'user.bob.ufolder 2.sub1',
#				'user.bob.ufolder 2.sub 2',
#			]
#		)
#
#	def test_newMailboxes(self):
#		self.assertEqual(
#			self.cyrus.newMailboxes,
#			[
#				'user.joe',
#				'user.joe.ufolder1',
#				'user.joe.ufolder1.sub1',
#				'user.joe.ufolder1.sub 2',
#				'user.joe.ufolder 2',
#				'user.joe.ufolder 2.sub1',
#				'user.joe.ufolder 2.sub 2',
#			]
#		)

#	def test_oldMailboxNameToNew(self):
#		self.assertEqual(self.cyrus.oldMailboxNameToNew('user.bob'), 'user.joe')
#		self.assertEqual(self.cyrus.oldMailboxNameToNew('user.bob.folder1'), 'user.joe.folder1')
#		self.assertEqual(self.cyrus.oldMailboxNameToNew('user.bob.folder 2'), 'user.joe.folder 2')

	def test_oldMailboxNameToNew_toVirtual(self):
		cyrus = CyrusMigrate(None, 'user.bob', 'user.tony@example.com')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob'), 'user.tony@example.com')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob.folder1'), 'user.tony.folder1@example.com')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob.folder 2'), 'user.tony.folder 2@example.com')

	def test_oldMailboxNameToNew_virtualToLocal(self):
		cyrus = CyrusMigrate(None, 'user.bob@example.com', 'user.tony')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob@example.com'), 'user.tony')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob.folder1@example.com'), 'user.tony.folder1')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob.folder 2@example.com'), 'user.tony.folder 2')

	def test_oldMailboxNameToNew_virtualToVirtual(self):
		cyrus = CyrusMigrate(None, 'user.bob@example.com', 'user.tony@other.net')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob@example.com'), 'user.tony@other.net')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob.folder1@example.com'), 'user.tony.folder1@other.net')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob.folder 2@example.com'), 'user.tony.folder 2@other.net')

	def test_oldMailboxNameToNew_localSharedToVirtual(self):
		cyrus = CyrusMigrate(None, 'user.bob', 'user.tony@example.com')
		self.assertEqual(cyrus.oldMailboxNameToNew('shared'), 'shared@example.com')
		self.assertEqual(cyrus.oldMailboxNameToNew('shared.sub'), 'shared.sub@example.com')

	def test_oldMailboxNameToNew_virtualSharedTolocal(self):
		cyrus = CyrusMigrate(None, 'user.bob@example.com', 'user.tony')
		self.assertEqual(cyrus.oldMailboxNameToNew('shared@example.com'), 'shared')
		self.assertEqual(cyrus.oldMailboxNameToNew('shared.sub@example.com'), 'shared.sub')

#	def test_partitionPath(self):
#		cyrus = CyrusMigrate(None, None, 'user.bob')
#		self.assertEqual(cyrus.newImapPartitionPath('user.bob'), '/var/spool/imap/user/bob')
#		self.assertEqual(cyrus.newImapPartitionPath('user.bob.folder 1'), '/var/spool/imap/user/bob/folder 1')
#		self.assertEqual(cyrus.newImapPartitionPath('user.bob.folder 1.sub'), '/var/spool/imap/user/bob/folder 1/sub')
	
	def test_partitionPath_virtual(self):
		cyrus = CyrusMigrate(None, None, 'user.bob')
		self.assertEqual(cyrus.newImapPartitionPath('user.bob@example.com'), '/var/spool/imap/domain/example.com/user/bob')
		self.assertEqual(cyrus.newImapPartitionPath('user.bob.folder 1@example.com'), '/var/spool/imap/domain/example.com/user/bob/folder 1')

	def test_configPath_user(self):
		cyrus = CyrusMigrate(None, None, 'user.bob')
		self.assertEqual(cyrus.newImapConfigPath('.seen'), '/var/lib/imap/user/b/bob.seen')

	def test_configPath_virtual(self):
		cyrus = CyrusMigrate(None, None, 'user.bob@example.net')
		self.assertEqual(cyrus.newImapConfigPath('.seen'), '/var/lib/imap/domain/e/example.net/user/b/bob.seen')
		self.assertRaises(Exception, cyrus.newImapConfigPath, 'shared.folder', '.seen')

	def test_mboxFromSubFormat(self):
		self.assertEqual(CyrusMigrate._mboxFromSubFormat('shared'), 'shared')
		self.assertEqual(CyrusMigrate._mboxFromSubFormat('user.bob'), 'user.bob')
		self.assertEqual(CyrusMigrate._mboxFromSubFormat('user.bob.folder 1'), 'user.bob.folder 1')
		self.assertEqual(CyrusMigrate._mboxFromSubFormat('example.com!user.bob'), 'user.bob@example.com')
		self.assertEqual(CyrusMigrate._mboxFromSubFormat('example.com!user.bob.folder 1'), 'user.bob.folder 1@example.com')

	def test__mboxToSubFormat(self):
		self.assertEqual(CyrusMigrate._mboxToSubFormat('shared'), 'shared')
		self.assertEqual(CyrusMigrate._mboxToSubFormat('user.bob'), 'user.bob')
		self.assertEqual(CyrusMigrate._mboxToSubFormat('user.bob.folder 1'), 'user.bob.folder 1')
		self.assertEqual(CyrusMigrate._mboxToSubFormat('user.bob@example.com'), 'example.com!user.bob')
		self.assertEqual(CyrusMigrate._mboxToSubFormat('user.bob.folder 1@example.com'), 'example.com!user.bob.folder 1')

