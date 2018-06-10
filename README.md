# Protocol Python Stubs Generator

Protoc by default doesn't provide typings or stub files for python. These are greatly improving code corectness, speed of development and helps a programmer to deliver higher quality product for lesser time.

This plugin is providing declarations in stub file of:
 - [X] message interface
 - [X] fields type
 - [X] constructor interface
 - [X] enumerator values
 - [X] nested messages interfaces

stored into `{PROTO_NAME}_pb2.pyi` and

 - [X] servicer interface
 - [X] stub interface
 - [X] `add_{SERVICER_NAME}_to_service` method interface

stored into `{PROTO_NAME}_pb2_grpc.pyi`.

## Installation

To install this plugin, just create a symbolic reference into the PATH directory to the both of the executable scripts:
```bash
$ sudo ln -s $(pwd)/protoc-gen-python_typings /usr/bin/protoc-gen-python_typings
$ sudo ln -s $(pwd)/protoc-gen-grpc_python_typings /usr/bin/protoc-gen-grpc_python_typings
```

## Usage

To use this plugin, just simple use `python_typings_out` parameter in `protoc` command, which can be use with standard `python_out` and `grpc_python_out` parameters:
```bash
$ protoc --python_out=./proto --grpc_python_out=./proto --python_typings_out=./proto --grpc_python_typings_out=./proto -I./proto ./proto/buffer.proto
```

The example was built with these options in a project directory:
```bash
$ protoc ./example/application.proto --python_typings_out=./example --python_out=./example --grpc_python_typings_out=./example --grpc_python_out=./example -I${GOPATH}/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis -I./example
```

## Goals

 - [X] extensible template background for both plugins
 - [X] working simple typing generator, that was protoc missing
 - [ ] generating proper type imports instead of provisional '*'
 - [ ] tests
 - [ ] setup.py
