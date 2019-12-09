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
    version="1.0.0-alpha-" + optional_git_version(),
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
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: C',
        'Programming Language :: C++',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
