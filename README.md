# Protocol Python Stubs Generator

Protoc by default doesn't provide typings or stub files for python. These are greatly improving code corectness, speed of development and helps a programmer to deliver higher quality product for lesser time.

This plugin is providing declarations in stub file of:
 - [X] message interface
 - [X] fields type
 - [X] constructor interface
 - [X] enumerator values
 - [X] nested messages interfaces

stored into `{PROTO_NAME}_pb2.pyi` and

 - [ ] servicer interface
 - [ ] stub interface
 - [ ] `add_{SERVICER_NAME}_to_service` method interface

stored into `{PROTO_NAME}_pb2_grpc.pyi`.

## Installation

To install this plugin, just copy it into the PATH directory:
```bash
$ sudo cp protoc-gen-python_typings /usr/bin/protoc-gen-python_typings
```

## Usage

To use this plugin, just simple use `python_typings_out` parameter in `protoc` command, which can be use with standard `python_out` and `grpc_python_out` parameters:
```bash
$ protoc --python_out=./proto --grpc_python_out=./proto --python_typings_out=./proto -I./proto ./proto/buffer.proto
```

The example was built with these options in project directory:
```bash
$ protoc ./example/application.proto --python_typings_out=./example --python_out=./example -I${GOPATH}/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis -I./example
```
