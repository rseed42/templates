# -*- coding: utf-8 -*-
# Copyright (c) 2014 'rseed42'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
This module contains rs.skels Python project templates
"""
import os
from setuptools import setup, find_packages
#-------------------------------------------------------------------------------
version = '0.2.4'
README = os.path.join(os.path.dirname(__file__),
                      'rseed42', 'skels', 'README.txt')
long_description = open(README).read() + '\n\n'
#-------------------------------------------------------------------------------
setup(name='rseed42.skels',
      version=version,
      description="Skeleton Python projects developed by rseed42",
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='rseed42',
      author_email='rseed42@gmail.com',
      url='http://rseed42.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rseed42'],
      include_package_data=True,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'PasteScript',
          'Cheetah',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.paster_create_template]
      rseed42_cmdline = rseed42.skels.templates:CmdLine
      rseed42_package = rseed42.skels.templates:Package
      """,
      )
