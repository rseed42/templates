from setuptools import setup, find_packages
version = '0.1.0'
classifiers = [
    "Programming Language :: Python",
    ("Topic :: Sofware Development :: "
     "Libraries :: Python Modules")]

setup(name='pbp.skels',
      version=version,
      description=("PasteScript templates for the Expert "
                   "Python programmin Book."),
      classifiers=classifiers,
      keywords='paste templates',
      author='rseed42',
      author_email='rseed42@gmail.com',
      url='http://rseed42.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pbp'],
      include_package_date=True,
      install_requres=['setuptools', 'PasteScript'],
      entry_points="""
      # -*- Entry points: -*-
      [paste.paster_create_template]
      pbp_package = pbp.skels.package:Package
      """)
