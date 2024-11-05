from setuptools import setup, find_packages

from server import __version__

setup(
    name='Spellbreak Server',
    version=__version__,
    packages=find_packages(),
    install_requires=[
        "tenacity",
    ],
    entry_points={
        'console_scripts': [
            'sb_server=server.server:main',
        ],
    },
)