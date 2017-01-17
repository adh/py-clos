from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="PyCLOS",
    version="0.2",
    author = "Ales Hakl",
    author_email = "ales@hakl.net",
    description = ("CLOS-style generic functions with annotation based syntax"),
    long_description=read('README.rst'),
    url="https://github.com/adh/py-clos",
    
    license="MIT",
    keywords="clos generic",

    packages=find_packages(),
    extras_require = {
        "lru": ["lru-dict"],
    },
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],    
)
