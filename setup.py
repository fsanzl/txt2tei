import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="txt2tei",
    version="1.0.2-2",
    python_requires='>=3.5',
    description="An aid to encoding plays as XML-TEI",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/fsanzl/txt2tei",
    project_urls={
        'Source': 'https://github.com/fsanzl/txt2tei/',
        'Tracker': 'https://github.com/fsanzl/txt2tei/issues',
    },
    author="Fernando Sanz-Lázaro",
    author_email="fsanzl@gmail.com",
    license="LGPL",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.5",
        "Natural Language :: Spanish",
    ],
    packages=["txt2tei"],
    entry_points={
        "console_scripts": [
            "txt2tei = txt2tei:main",
        ]
    },
    package_data={"": ["authors.xml", "sexos.csv"]},
    include_package_data=True,
)
