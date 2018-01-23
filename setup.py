import os
import sys

from setuptools import find_packages, setup


PACKAGE_DIR = 'src'


def get_version():
    from socketwhitelist import __version__
    return '.'.join(map(str, __version__))


try:
    version = get_version()
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), PACKAGE_DIR))
    version = get_version()


try:
    import multiprocessing
except ImportError:
    pass


install_requires = ['nose', 'future']
tests_require = ['nose']

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')


setup(
    name='nose-socket-whitelist',
    version=version,
    author='ted kaemming',
    author_email='ted@disqus.com',
    url='https://github.com/disqus/nose-socket-whitelist',
    license='Apache License 2.0',
    package_dir={'': PACKAGE_DIR},
    packages=find_packages(PACKAGE_DIR),
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    zip_safe=False,
    test_suite='nose.collector',
)
