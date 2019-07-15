!/usr/bin/env python
from setuptools import setup, find_packages
import os


data_files = [(d, [os.path.join(d, f) for f in files])
              for d, folders, files in os.walk(os.path.join('src', 'config'))]


setup(name='vmsd-parser',
      version='1.0',
      description='simple vmsd parser to help with VMWare Workstation Management',
      author='Adam Pridgen',
      author_email='adam.pridgen.phd@gmail.com',
      install_requires=[''],
      packages=find_packages('src'),
      package_dir={'': 'src'},
)
