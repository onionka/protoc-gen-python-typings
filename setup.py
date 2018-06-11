from setuptools import setup, find_packages

setup(
    name="ProtoC Python Typing generator plugin",
    version="0.1",
    packages=find_packages(),
    scripts=['protoc-gen-python_grpc_typings', 'protoc-gen-python_typings'],

    install_requires=['protobuf'],

    package_data={'stubs_generator': ['*.py']},

    # metadata for upload to PyPI
    author="Miroslav Cibulka",
    author_email="miroslav.cibulka@flowup.cz",
    description="ProtoC code generator plugin",
    license="MIT",
    keywords="proto3 typing python library script",
    url="https://github.com/Cmiroslaf/protoc-gen-python-typings",   # project home page, if any
    project_urls={
        "Bug Tracker": "https://github.com/Cmiroslaf/protoc-gen-python-typings/issues",
        "Documentation": "https://docs.example.com/HelloWorld/",
        "Source Code": "https://code.example.com/HelloWorld/",
    }

    # could also include long_description, download_url, classifiers, etc.
)
