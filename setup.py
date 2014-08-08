# coding: utf-8

from setuptools import setup, find_packages
import sys

from objectify import __version__

setup(
	name = 'objectify',
	version = __version__,
	description = 'Object library',
	author = 'William King',
	author_email = 'will@upout.com',
	zip_safe = False,
	include_package_data = True,
	packages=find_packages()
)