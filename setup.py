import sys

from setuptools import find_packages, setup

from socketwhitelist import __version__


try:
    import multiprocessing
except ImportError:
    pass


install_requires = ['nose']
tests_require = ['nose']

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')


setup(
    name='nose-socket-whitelist',
    version='.'.join(map(str, __version__)),
    author='ted kaemming',
    author_email='ted@disqus.com',
    url='https://github.com/disqus/nose-socket-whitelist',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    zip_safe=False,
    test_suite='nose.collector',
)
