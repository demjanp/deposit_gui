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
	install_requires=[
		'deposit==1.4.0',
		'networkx==2.6.3',
		'natsort==8.1.0',
		'Pillow==9.1.1',
		'PySide2==5.15.2.1',	
	],
	scripts=[],
	license='LICENSE',
	description='GUI for Deposit: Graph database focused on scientific data collection',
	long_description=open('README.md').read(),
	python_requires='>=3.10',
)
