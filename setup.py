# coding=utf-8
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'paginate',
    'paginate_sqlalchemy',
    'passlib',

    'future',
    'psycopg2',
    'markdown',
    'wtforms',
    ]



tests_require = ['pytest-cov', 'webtest', 'tox']

dev_requires = ['ipython', 'pyramid-ipython']

setup(name='learning-journal',
      version='0.0',
      description='CodeFellows 401 Learning journal',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Hannah Krager',
      author_email='hannahkrager@gmail.com',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='learning-journal',
      install_requires=requires,
      extras_require={
        'test': tests_require,
        'dev': dev_requires,
      },
      entry_points="""\
      [paste.app_factory]
      main = learning_journal:main
      [console_scripts]
      initialize_db = learning_journal.scripts.initializedb:main
      get_posts_api = learning_journal.scripts.api_script:main
      """,
      )
