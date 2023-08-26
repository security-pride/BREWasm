# setup.py
from setuptools import setup, find_packages

with open('README.md', encoding='UTF-16LE') as f:
  long_description = f.read()

setup(name='BREWasm',
      version='1.0.5',
      description='A general purpose static binary rewriting framework for Wasm, which aims at reducing the complexity of the Wasm',
      long_description=long_description,
      install_requires=[
        "cyleb128",
      ],
      long_description_content_type='text/markdown',
      packages=find_packages(),
      url='https://github.com/BREWasm/brewasm-project',
      author='BREWasm',
      license='MIT',
      keywords=['BINARY', 'REWRITER', 'WASM'],
      data_files=[('images', ['doc/Definition.png'])],
      )