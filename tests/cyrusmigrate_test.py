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
		}

	def lm(self, mailbox):
		return self._mailboxes.get(mailbox, [])

	def reconstruct(self, mailbox):
		pass

	def cm(self, mailbox):
		pass


class Test_CyrusMigrate(unittest.TestCase):
	""" Test basic SignalRecorder class
	"""
	def test_mailboxParts_userLocal(self):
		self.assertEqual(CyrusMigrate._mailboxParts('user.joe'), ('user.joe', None))
		self.assertEqual(CyrusMigrate._mailboxParts('user.joe.myMail'), ('user.joe.myMail', None))

	def test_mailboxParts_userVirtual(self):
		self.assertEqual(CyrusMigrate._mailboxParts('user.joe@example.com'), ('user.joe', 'example.com'))
		self.assertEqual(CyrusMigrate._mailboxParts('user.joe.myMail@example.com'), ('user.joe.myMail', 'example.com'))

	def test_mailboxParts_sharedLocal(self):
		self.assertEqual(CyrusMigrate._mailboxParts('sharedMbox'), ('sharedMbox', None))
		self.assertEqual(CyrusMigrate._mailboxParts('sharedMbox.another'), ('sharedMbox.another', None))

	def test_mailboxParts_sharedVirtual(self):
		self.assertEqual(CyrusMigrate._mailboxParts('sharedMbox@example.com'), ('sharedMbox', 'example.com'))
		self.assertEqual(CyrusMigrate._mailboxParts('sharedMbox.another@example.com'), ('sharedMbox.another', 'example.com'))

	def test_listMailboxes(self):
		imap = MockImap()
		cyrus = CyrusMigrate(imap, None, None)
		self.assertEqual(
			cyrus.listMailboxes('user.bob'),
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
		self.assertEqual(
			cyrus.listMailboxes('user.bob@example.com'),
			[
				'user.bob@example.com',
				'user.bob.vfolder1@example.com',
				'user.bob.vfolder1.sub1@example.com',
				'user.bob.vfolder1.sub 2@example.com',
				'user.bob.vfolder 2@example.com',
				'user.bob.vfolder 2.sub1@example.com',
				'user.bob.vfolder 2.sub 2@example.com',
			]
		)
		self.assertEqual(
			cyrus.listMailboxes('user.toby@example.com'),
			[]
		)
		self.assertEqual(
			cyrus.listMailboxes('user.toby'),
			[]
		)

	def test_oldMailboxNameToNew_localToLocal(self):
		cyrus = CyrusMigrate(None, 'user.bob', 'user.tony')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob'), 'user.tony')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob.folder1'), 'user.tony.folder1')
		self.assertEqual(cyrus.oldMailboxNameToNew('user.bob.folder 2'), 'user.tony.folder 2')

	def test_oldMailboxNameToNew_localToVirtual(self):
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

	def test_partitionPath(self):
		self.assertEqual(CyrusMigrate._imapPartitionPath('user.bob'), '/var/spool/imap/user/bob')
		self.assertEqual(CyrusMigrate._imapPartitionPath('user.bob.folder 1'), '/var/spool/imap/user/bob/folder 1')
		self.assertEqual(CyrusMigrate._imapPartitionPath('user.bob.folder 1.sub'), '/var/spool/imap/user/bob/folder 1/sub')
		self.assertEqual(CyrusMigrate._imapPartitionPath('user.bob@example.com'), '/var/spool/imap/domain/example.com/user/bob')
		self.assertEqual(CyrusMigrate._imapPartitionPath('user.bob.folder 1@example.com'), '/var/spool/imap/domain/example.com/user/bob/folder 1')

	def test_configPath(self):
		self.assertEqual(CyrusMigrate._imapConfigPath('user.bob', '.seen'), '/var/lib/imap/user/b/bob.seen')
		self.assertEqual(CyrusMigrate._imapConfigPath('user.bob@example.net', '.seen'), '/var/lib/imap/domain/e/example.net/user/b/bob.seen')
		self.assertRaises(Exception, CyrusMigrate._imapConfigPath, 'shared.folder', '.seen')

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

