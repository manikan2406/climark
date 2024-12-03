from setuptools import setup, find_packages

setup(
    name="ollama-cli-markdown-generator",
    version="1.0.0",
    author="manikan2406",
    author_email="manikandan.c@eminds.ai",
    description="A CLI tool for generating and validating test cases using Ollama LLM",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/manikan2406/cli-markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "langchain-core",
        "langchain-ollama",
        "pytest",
        "torch",
        "transformers",
        "markdown"
    ],
    entry_points={
    "console_scripts": [
        "ollama-cli-markdown-generator=markdown:main",
    ],
},

    extras_require={
        "dev": ["pytest"],
    },

   classifiers=[
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
],

    include_package_data=True,
    zip_safe=False,
)
