import os
from setuptools import setup, find_packages

VERSION = (0, 2)

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='python-cielo',
    version='.'.join(map(str, VERSION)),
    description='python-cielo is a lightweight lib for making payments over the Cielo webservice (Brazil)',
    long_description=readme,
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='cielo e-commerce',
    author='Renato Pedigoni',
    author_email='renatopedigoni@gmail.com',
    url='http://github.com/rpedigoni/python-cielo',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['requests'],
)
