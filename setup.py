from distutils.core import setup

setup(
    name='lockercli',
    version='0.3.5',
    author='Benjamin Allan-Rahill, Intern',
    author_email='benjamin.allan-rahill@bms.com',
    packages=['lockercli'],
    entry_points = { 'console_scripts': [ 'locker=locker.cli:main', ], },
    description='A command line interface for running environments on your local machine',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=open('requirements.txt').read().split(),
    zip_safe=False
)