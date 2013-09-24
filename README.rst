cyrus miration utilites
-----------------------

Cyrus imap mailbox migration utilities.

Uses:

    Cyrus Imapd Skiplist db recovery tool
    Copyright (C) 2004-2006 Gianluigi Tiesi <sherpya@netfarm.it>
    Copyright (C) 2004-2006 NetFarm S.r.l.  [http://www.netfarm.it]

    Cyruslib v0.8.5-20090401
    Copyright (C) 2007-2009 Reinaldo de Carvalho <reinaldoc@gmail.com>
    Copyright (C) 2003-2006 Gianluigi Tiesi <sherpya@netfarm.it>
    Copyright (C) 2003-2006 NetFarm S.r.l. [http://www.netfarm.it]


About
=====
This utility migrates cyrus imap mailboxes from one format to another. The following
types are supported:

*   local user mailbox
*   virtual user mailbox (domain)
*   shared mailboxes (both local and virtual)

I wrote this utility because I was changing host providers where I run my small mailserver for a
bunch of accounts (<50), and at the same time I wanted to change the type of account from local
users to virtual users. The mailserver hosts a varitey of different domains and it made sense to
partition all users into their respective domains. So instead of users authenticating with
usernames "bobj" and "bobw", they would use "bob@example.com" and "bob@other.com".

Doing the migration whilst maintaining a service is a challenge, so I needed a utility that would
automate the migration for me that could be run and re-run until the final DNS switch was made.

Syncing old mailboxes to new host
=================================

The following rsync command (in python) will pull over all relevant files from `oldmailhost` onto
the current host. Because I was migrating from local user to vurtal user , I just needed the
mailbox files from /var/spool/imap and the metadata files from /var/lib/imap/user:

    import subprocess
    subprocess.check_call([
        'rsync',
        '--verbose',
        '--archive',
        '--compress',
        '--relative',
        '--delete',
        '--exclude=cyrus.*',
        'oldmailhost:/var/spool/imap',
        'oldmailhost:/var/lib/imap/user',
        '/'
    ])


Next, the CyrusMigrate utility is called for each account to migrate:

