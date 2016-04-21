import codecs
import os
import re
from setuptools import setup


def abs_path(*relative_path_parts):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        *relative_path_parts)


def read(f):
    with open(abs_path(f)) as fp:
        return fp.read().strip()


name = 'aiojsonrpc'

subpackages = ['{}.{}'.format(name, subpkg)
               for subpkg in ['serializer', ]]

packages = [name, ] + subpackages

install_requires = [
    'aiohttp>=0.21.5',
    'ujson>=1.35',
    'msgpack-python>=0.4.7',
]


setup_requires = [
    'pytest-runner>=2.7',
]

tests_require = [
    'pytest>=2.9.0',
    'pytest-asyncio>=0.3.0',
    'pytest-cov>=2.2.1',
]


with codecs.open(abs_path(name, '__init__.py'), 'r', 'utf-8') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'.*?$",
                             fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

author = 'Eugene Naydenov'
author_email = 't.34.oxygen+github+{}@gmail.com'.format(name)

maintainer = author
maintainer_email = author_email

setup(
    name=name,
    version=version,
    description=('JSON-RPC library to use in asynchronous JSON-RPC services'),
    long_description=read('README.rst'),
    author=author,
    author_email=author_email,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    url='https://github.com/f0t0n/aiojsonrpc/',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    license='Apache 2',
    packages=packages,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    include_package_data=True,
)
