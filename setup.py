import sys
from setuptools import setup

setup(name='cyrusmigrate',
	version="1.0",
	description='Utility to convert cyrus imap accounts',
#	long_description=readme(),
	url='http://github.com/innerhippy/pydosh',
	author='Will Hall',
	author_email='will@innerhippy.com',
	license='GPLv3',
	packages=['cyrusmigrate'],
	zip_safe=False,
	test_suite='tests',
)
