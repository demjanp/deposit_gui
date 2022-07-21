# -*- coding: utf-8 -*-
#!/usr/bin/env python
#

from setuptools import setup, find_packages

from deposit_gui import __version__

setup(
	name='deposit_gui',
	version=__version__,
	author='Peter Demján',
	author_email='peter.demjan@gmail.com',
	packages=find_packages(include = ['deposit_gui', 'deposit_gui.*']),
	install_requires=[],
	scripts=[],
	license='LICENSE',
	description='GUI for Deposit - Graph-based data storage and exchange',
	long_description=open('README.md').read(),
	python_requires='>=3.10',
)
