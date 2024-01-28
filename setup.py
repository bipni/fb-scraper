from setuptools import find_packages, setup

setup(
    name='fb-scraper',
    version='0.0',
    author='Mirja Wakil',
    description='A minimal facebook scraper',
    packages=find_packages(),
    install_requires=[
        'bs4==0.0.2',
        'python-dateutil==2.8.2',
        'requests==2.31.0',
        'requests-html==0.10.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    license='MIT',
    keywords='facebook scraper',
)
