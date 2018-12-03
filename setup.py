from os import path
from io import open
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file.
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Quom',
    version='0.1.0',
    url='https://github.com/Viatorus/quom',
    license='MIT',

    author='Toni Neubert',
    author_email='lutztonineubert@gmail.com',

    description='Quom is a single header generator for C/C++ libraries.',
    long_description=long_description,

    packages=find_packages(exclude=('tests',)),

    install_requires=[],

    zip_safe=False,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ],
)
