from setuptools import setup, find_packages

setup(
    name="python-music-player",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.0.0",
        "mutagen>=1.45.0",
        "Pillow>=8.0.0"
    ],
    entry_points={
        'console_scripts': [
            'pymusic=main:main',
        ],
    },
)