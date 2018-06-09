from typing import List, Type, cast

from .bases import CodePart, FieldType


class ConstantPart(CodePart):
    def __init__(self, const_data: str):
        self._data = const_data

    def generate(self, indentation: int, indentation_str: str):
        return self._data.format(
            indent=indentation_str * indentation,
            indent_inner=indentation_str * (indentation + 1)
        )


ConstantPart = cast(Type[CodePart], ConstantPart)

NEW_LINE = ConstantPart("\n")
NO_OP = ConstantPart("{indent}pass\n")


class EnumValue(CodePart):
    TEMPLATE = """\
{indent}{name}: int = {value}
"""

    def __init__(self, name: str, value: int):
        self._name = name
        self._value = value

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            value=self._value,
            indent=indentation_str * indentation
        )


class Field(CodePart):
    TEMPLATE = """\
{indent}{name}: {type} = ...
"""

    def __init__(self, value_type: FieldType, name: str):
        self._type = value_type
        self._name = name

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            type=self._type.generate(),
            indent=indentation_str * indentation
        )


class ConstructorParameter(CodePart):
    TEMPLATE = """\
{indent}{name}: {type} = None,
"""

    def __init__(self, value_type: FieldType, name: str):
        self._type = value_type
        self._name = name

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            type=self._type.generate(),
            indent=indentation_str * indentation
        )


class Constructor(CodePart):
    TEMPLATE = """
{indent}def __init__(self{args}):
{indent_inner}pass
"""

    def __init__(self, *args: ConstructorParameter):
        self._args = args

    def generate(self, indentation: int, indentation_str: str):
        return self.TEMPLATE.format(
            args=(
                ",\n" + "".join(
                    " " * 13 + a.generate(indentation, indentation_str)
                    for a in self._args
                )[:-2] if self._args else ""
            ),
            indent=indentation_str * indentation,
            indent_inner=indentation_str * (indentation + 1)
        )


class Message(CodePart):
    TEMPLATE = """\
{indent}class {class_name}(Message):
{fields}
{indent_inner}# region <<<Message Implementation>>>
{indent_inner}def __eq__(self, other_msg: '{parent_path}{class_name}') -> bool: ...
{indent_inner}def __str__(self) -> str: ...
{indent_inner}def __unicode__(self) -> str: ...
{indent_inner}def MergeFrom(self, other_msg: '{parent_path}{class_name}'): ...
{indent_inner}def Clear(self): ...
{indent_inner}def SetInParent(self): ...
{indent_inner}def IsInitialized(self) -> bool: ...
{indent_inner}def MergeFromString(self, serialized: str): ...
{indent_inner}def SerializeToString(self, **kwargs) -> str: ...
{indent_inner}def SerializePartialToString(self, **kwargs) -> str: ...
{indent_inner}def ListFields(self) -> List[FieldDescriptor]: ...
{indent_inner}def HasField(self, field_name: str) -> bool: ...
{indent_inner}def ClearField(self, field_name: str): ...
{indent_inner}def WhichOneof(self, oneof_group: str): ...
{indent_inner}def HasExtension(self, extension_handle: str) -> bool: ...
{indent_inner}def ClearExtension(self, extension_handle): ...
{indent_inner}def DiscardUnknownFields(self): ...
{indent_inner}def ByteSize(self) -> int: ...
{indent_inner}def _SetListener(self, message_listener): ...

{indent_inner}# endregion <<<Message Implementation>>>
{indent_inner}...
"""

    def __init__(self, name: str, parents: List[str], *inner: CodePart):
        self._name = name
        self._parent_path = ".".join(parents) + ("." if parents else "")

        self._inner = list(inner)
        if not self._inner:
            self._inner.append(NO_OP)

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            class_name=self._name,
            parent_path=self._parent_path,
            fields="".join(i.generate(indentation + 1, indentation_str) for i in self._inner),
            indent=indentation_str * indentation,
            indent_inner=indentation_str * (indentation + 1)
        )


class Import(CodePart):
    IMPORT_FROM_TEMPLATE = """\
{indent}from {path} import {items}
"""
    IMPORT_TEMPLATE = """\
{indent}import {path}
"""

    def __init__(self, path: str, items: List[str] = None):
        # replace `.proto` with `_pb2` name suffix that is used in python generated files
        # but in imports `.py` is omitted
        if path.endswith('.proto'):
            path = path[:-6] + "_pb2"
        # this is relative path to the known paths in `PYTHONPATH` environment variable
        # so we just need to replace / for . to get it work
        if '/' in path:
            path = path.replace('/', '.')
        self._path = path
        self._from_items = ", ".join(items) if items else None

    def generate(self, indentation: int, indentation_str: str) -> str:
        if self._from_items:
            return self.IMPORT_FROM_TEMPLATE.format(
                path=self._path,
                items=self._from_items,
                indent=indentation_str * indentation
            )
        return self.IMPORT_TEMPLATE.format(
            path=self._path,
            indent=indentation_str * indentation
        )

    # region <<<Comparison operators for sorting>>>
    def __lt__(self, other: 'Import') -> bool:
        return self._path < other._path

    def __gt__(self, other: 'Import') -> bool:
        return self._path > other._path

    def __eq__(self, other: 'Import') -> bool:
        return self._path == other._path

    def __le__(self, other: 'Import') -> bool:
        return self._path <= other._path

    def __ge__(self, other: 'Import') -> bool:
        return self._path >= other._path

    def __ne__(self, other: 'Import') -> bool:
        return self._path != other._path

    # endregion
    ...


class File(CodePart):
    """File holds all parts together and its generate method will run recursive
       stub generation with certain indentation
    """
    def __init__(self, *inners: CodePart):
        self._inners = list(inners)

    def generate(self, indentation: int, indentation_str: str) -> str:
        return "".join(i.generate(indentation, indentation_str) for i in self._inners)
