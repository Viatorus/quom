from os import path
from io import open
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file.
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Quom',
    version='1.1.0',
    url='https://github.com/Viatorus/quom',
    license='MIT',

    author='Toni Neubert',
    author_email='lutztonineubert@gmail.com',

    description='Quom is a single header generator for C/C++ libraries.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=find_packages(exclude=('tests',)),

    install_requires=[],

    zip_safe=False,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ],

    entry_points={
        'console_scripts': [
            'quom=quom.__main__:main',
        ]
    },
)
