from setuptools import setup

PACKAGE = 'tracmailman'
VERSION = '0.4.1'
SUMMARY = 'A Trac plugin integrating searching of Mailman archives.'
AUTHOR = 'Theron Ji, Spencer Fang, Benjamin Weaver'
EMAIL = 'baweaver@lbl.gov'


setup(name=PACKAGE,
    version=VERSION,
    description=SUMMARY,
    author=AUTHOR,
    author_email=EMAIL,
    packages=['tracmailman'],
    package_data={PACKAGE : ['templates/*.html']},
    entry_points={'trac.plugins': 'tracmailman.web_ui = tracmailman.web_ui'},
)
