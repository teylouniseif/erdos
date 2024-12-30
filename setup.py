from setuptools import setup, find_packages

setup(
    name="erdos",
    version="0.1.0",
    author="Saif Kurdi-Teylouni",
    author_email="teylouniseif@gmail.com",
    description="A math conversational API, handling concurrent conversations in real time",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/teylouniseif/erdos",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai",
        "pytest-asyncio",
        "langchain",
        "langchain-community",
        "langchain-core",
        "langchain-openai",
        "langchain-text-splitters",
        "autopep8",
        "pytest",
        "pre-commit"
    ],
)
