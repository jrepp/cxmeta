import subprocess
from setuptools import setup, find_packages


DESCRIPTION = 'A python CLI and library to extract \
meta-data from Cxx style languages.'


def read_git_version():
    proc = subprocess.Popen(
        ['git', 'rev-parse', '--short', 'HEAD'],
        stdout=subprocess.PIPE)
    buffer = []
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        buffer.append(line.rstrip())
    return ''.join(buffer)


def optional_git_version():
    try:
        git_version = read_git_version()
        if git_version:
            return "-" + git_version
    except:
        pass
    return ""


setup(
    name="cxmeta",
    version="0.1" + optional_git_version(),
    packages=find_packages(),
    scripts=['cxmeta/tools/cli.py'],
    install_requires=[
        'docopt',
        'docutils',
    ],
    package_data={
        '': ['*.md', '*.rst']
    },
    entry_points={
        'console_scripts': ['cxmeta=cxmeta.tools.cli:main'],
    },
    author='Jacob Repp',
    author_email='jacobrepp@gmail.com',
    description=DESCRIPTION,
    keywords='Cxx C C++ documentation docs rst markdown build',
    url='https://github.com/jrepp/cxmeta',
    project_urls={
        'Source Code': 'https://github.com/jrepp/cxmeta'
    },
    classifiers=[
        'License :: LGPL 3.0 ::',
    ]
)
