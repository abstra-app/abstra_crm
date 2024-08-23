import os
import pathlib
import re

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding="utf-8")

# The list of requirements
REQUIREMENTS = (HERE / "requirements.txt").read_text(encoding="utf-8").split("\n")


setup(
    name="abstra_crm",
    license="MIT",
    version="0.0.0",
    python_requires=">=3.8, <4",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    install_requires=REQUIREMENTS,
)