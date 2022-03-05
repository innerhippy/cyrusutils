from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='cyrusutils',
	version="1.2",
	description='Cyrus imap account conversion utilities',
	long_description=readme(),
	url='http://github.com/innerhippy/cyrusutils',
	author='Will Hall',
	author_email='will@innerhippy.com',
	license='GPLv3',
	packages=['cyrusutils'],
	scripts=['scripts/cyrusmigrate'],
	zip_safe=False,
	test_suite='tests',
)
