import os
import re
from distutils.core import setup

tests_require = [
    'pytest',
    'pytest-cov'
]

install_requires = [
    'biopython',
    'marshmallow',
    'pyblast',
    'networkx'
]


def sanitize_string(str):
    str = str.replace('\"', '')
    str = str.replace("\'", '')
    return str


def parse_version_file():
    """Parse the __version__.py file"""
    here = os.path.abspath(os.path.dirname(__file__))
    ver_dict = {}
    with open(os.path.join(here, 'dasi', '__version__.py'), 'r') as f:
        for line in f.readlines():
            m = re.match('__(\w+)__\s*=\s*(.+)', line)
            if m:
                ver_dict[m.group(1)] = sanitize_string(m.group(2))
    return ver_dict



ver = parse_version_file()

# setup
setup(
    title=ver['title'],
    name=ver['title'],
    version=ver['version'],
    packages=["dasi"],
    url=ver['url'],
    license='',
    author=ver['author'],
    author_email='',
    keywords='DNA Assembler',
    description=ver['description'],
    install_requires=install_requires,
    python_requires='>=3.6',
    tests_require=tests_require,
)
