import sys
from setuptools import setup

setup(name='cyrusutils',
	version="1.0",
	description='Cyrus imap account conversion utilities',
	url='http://github.com/innerhippy/cyrusutils',
	author='Will Hall',
	author_email='will@innerhippy.com',
	license='GPLv3',
	packages=['cyrusutils'],
	scripts=['scripts/cyrusmigrate'],
	zip_safe=False,
	test_suite='tests',
)
