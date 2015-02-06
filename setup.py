from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='iol.gisweb.spezia',
      version=version,
      description="Application for Iol Project Spezia",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='plone iol spezia',
      author='Marco Carbone',
      author_email='marco.carbone@gmx.com',
      url='https://github.com/mamogmx/iol.gisweb.spezia.git',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gisweb', 'gisweb.iol'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.api',
          'Products.CMFPlomino',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
