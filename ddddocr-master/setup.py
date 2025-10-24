#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/2 15:41
# @Author  : sml2h3
# @Site    :
# @File    : setup.py
# @Software: PyCharm
# @Description:

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ddddocr",
    version="1.6.0",
    author="sml2h3",
    description="带带弟弟OCR",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sml2h3/ddddocr",
    packages=find_packages(where='.', exclude=(), include=('*',)),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy', 'onnxruntime', 'Pillow', 'opencv-python-headless'],
    extras_require={
        'api': ['fastapi>=0.100.0', 'uvicorn[standard]>=0.20.0', 'pydantic>=2.0.0'],
        'all': ['fastapi>=0.100.0', 'uvicorn[standard]>=0.20.0', 'pydantic>=2.0.0']
    },
    python_requires='<=3.13',
    include_package_data=True,
    install_package_data=True,
    entry_points={
        'console_scripts': [
            'ddddocr=ddddocr.__main__:main',
        ],
    },
)
