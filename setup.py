from setuptools import setup


setup(
    name='licenselib',
    version='1.0',
    license='BSD',
    author='William Grzybowski',
    author_email='wg@FreeBSD.org',
    description='FreeNAS/TrueNAS License library',
    platforms='any',
    packages=('licenselib', ),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
)
