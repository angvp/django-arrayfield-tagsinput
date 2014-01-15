# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

required = [
    'djorm-ext-pgarray',
]

def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='arrayfield_tagsinput',
    version=__import__('arrayfield_tagsinput').__version__,
    author=u'Ángel Velásquez, Agustín Cangiani',
    author_email='angvp@archlinux.org, cangiani@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='http://www.routeatlas.com',
    license='GPL',
    description=u' '.join(__import__('arrayfield_tagsinput').__doc__.splitlines()).strip(),
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    install_requires=required,
    long_description=read_file('README.rst'),
    test_suite="runtests.runtests",
    zip_safe=False,
)
