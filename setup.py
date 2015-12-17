try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sdk_updater

requires = [
    'jprops',
    'pexpect',
    'semantic_version',
]

setup(
    name='android-sdk-updater',
    version=sdk_updater.__version__,
    description='A command-line utility for keeping your Android dependencies up-to-date.',
    long_description=open('README.rst').read(),
    keywords='android',
    license=open('LICENSE').read(),
    author='Tad Fisher',
    author_email='tadfisher@gmail.com',
    url='https://github.com/tadfisher/android-sdk-updater',
    install_requires=requires,
    packages=['sdk_updater'],
    scripts=['bin/android-sdk-updater'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools'
    ]
)
