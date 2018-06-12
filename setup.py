from setuptools import setup

setup(
    name="ProtoC Python Typing generator plugin",
    version="0.2",

    install_requires=['protobuf'],

    scripts=['protoc-gen-python_grpc_typings', 'protoc-gen-python_typings'],
    packages=['stubs_generator'],

    # metadata for upload to PyPI
    author="Miroslav Cibulka",
    author_email="miroslav.cibulka@flowup.cz",
    description="ProtoC code generator plugin",
    license="MIT",
    keywords="proto3 typing python library script",
    url="https://github.com/Cmiroslaf/protoc-gen-python-typings",  # project home page, if any
    project_urls={
        "Bug Tracker": "https://github.com/Cmiroslaf/protoc-gen-python-typings/issues",
        "Documentation": "https://docs.example.com/HelloWorld/",
        "Source Code": "https://code.example.com/HelloWorld/",
    }

    # could also include long_description, download_url, classifiers, etc.
)
