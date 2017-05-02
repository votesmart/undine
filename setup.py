import os.path
from setuptools import setup, find_packages

__DIR__ = os.path.abspath(os.path.dirname(__file__))

setup(
    name = 'undine',
    version = '0.0.1',
    description = 'A wrapper for handling multi-archive backups with Borg',
    url = 'https://github.com/votesmart/undine',
    author = 'Mike Shultz',
    author_email = 'mike@votesmart.org',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Archiving :: Backup',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords = 'backup borg',
    packages = find_packages(),
    install_requires = open("requirements.txt").readlines(),
    entry_points={
        'console_scripts': [
            'undine=undine:main',
        ],
    },
)