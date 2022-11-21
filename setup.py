# -*- coding: utf-8 -*-
#!/usr/bin/env python
#

from setuptools import setup, find_packages

import pathlib

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False
except ImportError:
    bdist_wheel = None

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="deposit_gui",
    version="1.4.34",
    description="GUI for Deposit: Graph database focused on scientific data collection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/demjanp/deposit_gui",
    author="Peter Demjan",
    author_email="peter.demjan@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Database",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
    keywords="database, graph",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
	package_data={"":[
		"*.dll",
		"*.exe",
		"*.sh",
		"config6",
		"*.c",
		"*.i",
		"INSTALLER",
		"LICENSE",
		"METADATA",
		"*.pyd",
		"*.png",
		"*.svg",
	]},
    python_requires=">=3.10, <4",
	install_requires=[
		'deposit>=1.4.31, <1.5',
		'svgelements>=1.8.1, <2',
	],
	cmdclass={'bdist_wheel': bdist_wheel},
)
