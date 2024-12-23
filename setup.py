'''
Author: ping ping 51507451+abc767234318@users.noreply.github.com
Date: 2024-11-28 19:42:31
LastEditors: ping ping 51507451+abc767234318@users.noreply.github.com
LastEditTime: 2024-11-28 19:58:16
FilePath: \BREWasm\setup.py
Description: 

Copyright (c) 2024 by ${git_name_email}, All Rights Reserved. 
'''
# setup.py
from setuptools import setup, find_packages

with open('README.md', encoding='UTF-16LE') as f:
  long_description = f.read()

setup(name='BREWasm',
      version='1.0.9',
      description='A general purpose static binary rewriting framework for Wasm, which aims at reducing the complexity of the Wasm',
      long_description=long_description,
      install_requires=[
        "cyleb128",
      ],
      long_description_content_type='text/markdown',
      packages=find_packages(),
      url='https://github.com/security-pride/BREWasm',
      author='BREWasm',
      license='MIT',
      keywords=['BINARY', 'REWRITER', 'WASM'],
      data_files=[('images', ['doc/Definition.png'])],
      )