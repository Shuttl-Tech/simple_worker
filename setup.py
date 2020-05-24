from setuptools import setup
from setuptools import find_packages

setup(
    name="simple_worker",
    version="0.2.21",
    description="A task queues library that uses AWS SQS",
    url="https://github.com/shuttl-tech/simple_worker",
    author="Paul Kuruvilla",
    author_email="paul.kuruvilla@shuttl.com",
    license="MIT",
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3.7"],
    install_requires=["boto3", "tenacity"],
    extras_require={"test": ["pytest", "pytest-runner", "pytest-cov", "tenacity"]},
)
