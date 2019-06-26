from distutils.core import setup
setup(
    name='fgdtools',
    packages=['fgdtools'],
    version='0.1',
    license='gpl-3.0',
    description='A library to parse .fgd files used for the source engine.',
    author='Maxime Dupuis',
    author_email='mdupuis@hotmail.ca',
    url='https://github.com/maxdup/fgd-tools',
    # download_url='https://github.com/user/reponame/archive/v_01.tar.gz',
    keywords=['fgd', 'source', 'hammer'],
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3.0',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
