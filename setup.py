from setuptools import setup, find_packages

setup(
    name="file_organizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PySimpleGUI>=4.60.5",
        "pathlib>=1.0.1",
        "pillow>=10.0.0",
        "send2trash>=1.8.2",
        "loguru>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "file_organizer=src.main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A file management automation tool",
    keywords="file, organization, automation, utility",
    python_requires=">=3.7",
)