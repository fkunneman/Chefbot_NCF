#! /usr/bin/env python3

import os
import sys
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Chefbot_NCF",
    version = "0.1",
    author = "Florian Kunneman",
    author_email = "f.a.kunneman@vu.nl",
    description = ("Framework for managing conversational agents"),
    license = "GPL",
    keywords = "conversational_ai cooking_assistant",
    url = "https://github.com/fkunneman/Chefbot_NCF.git",
    packages=['Chefbot_NCF','Chefbot_NCF.core'],
    package_data={'Chefbot_NCF' : ['example_data/*.json']},
    #,'Chefbot_NFC', 'Chefbot_NFC.core'],
    #data_files=[('example_data', ['Chefbot_NFC/example_data/*.json'])],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Conversational AI :: Text Processing :: Cooking Assistant",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    include_package_data=True,
#    package_data = {'example_data': ['*.json'] },
    zip_safe=False,
    install_requires=[],
)
