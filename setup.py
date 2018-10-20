from setuptools import setup

setup(
    name='simple_worker',
    version='0.1',
    description='A task queues library that uses AWS SQS',
    url='https://github.com/shuttl-tech/simple_worker',
    author='Paul Kuruvilla',
    author_email='paul.kuruvilla@shuttl.com',
    license='MIT',
    packages=['simple_worker'],
    classifiers=["Programming Language :: Python :: 3.7"],
    install_requires=['boto3'],
    tests_requires=['pytest', 'pdb'])
