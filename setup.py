from setuptools import setup, find_packages
setup(
    name="cxmeta",
    version="0.1",
    packages=find_packages(),
    scripts=['cxmeta/tools/cli.py'],
    install_requires=[
        'docopt',
        'docutils',
    ],
    package_data={
        '': ['*.md', '*.rst']
    },
    entry_points = {
        'console_scripts': ['cxmeta=cxmeta.tools.cli:main'],
    },
    author='Jacob Repp',
    author_email='jacobrepp@gmail.com',
    description='A python CLI and library to extract meta-data from Cxx style languages.',
    keywords='Cxx C C++ documentation docs rst markdown build',
    url='https://github.com/jrepp/cxmeta',
    project_urls={
        'Source Code': 'https://github.com/jrepp/cxmeta'
    },
    classifiers=[
        'License :: LGPL 3.0 ::',
    ]
)
