from typing import List, Optional, Union

from .base import CodePart, FieldType, NEW_LINE, NO_OP


class EnumValue(CodePart):
    TEMPLATE = """{indent}{name}: int = {value}"""

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
    TEMPLATE = """{indent}{name}{type} = {value}"""

    def __init__(self, value_type: Optional[FieldType], name: str, value: str = "..."):
        self._type = value_type
        self._name = name
        self._value = value

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            value=self._value,
            type=": {}".format(self._type.generate()) if self._type else "",
            indent=indentation_str * indentation
        )


class FieldComment(CodePart):
    TEMPLATE = """{indent}:param {name}:{comment}{multiline_comment}"""

    def __init__(self, name: str, comment: List[str]):
        self._name = name
        self._comment = comment
        self._multiline_comment = "\n{indent}       " + " " * len(self._name) + "  {comment}"

    @property
    def has_comment(self):
        return bool(self._comment)

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            comment=self._comment[0],
            multiline_comment=(
                "".join(self._multiline_comment.format(comment) for comment in self._comment[1:])
                if self._comment else
                ""
            ),
            indent=indentation_str * indentation
        ) if self._comment else ""


class ConstructorParameter(FieldType):
    TEMPLATE = """{name}: {type} = None"""

    def __init__(self, value_type: FieldType, name: str, comment: List[str]):
        self._type = value_type
        self._name = name
        self._comment = comment

    def to_field(self) -> Field:
        return Field(None, "self.{}".format(self._name), self._name)

    def to_field_comment(self) -> FieldComment:
        return FieldComment(self._name, self._comment)

    def generate(self) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            type=self._type.generate()
        )


class Constructor(CodePart):
    TEMPLATE = """\
{indent}def __init__(self{args}):{comments}
{fields}
"""
    ARG_SEPARATOR_TEMPLATE = """,
{indent}             """

    def __init__(self, *args: ConstructorParameter):
        self._args = args

    def generate(self, indentation: int, indentation_str: str):
        param_separator = self.ARG_SEPARATOR_TEMPLATE.format(indent=indentation_str * indentation)
        return self.TEMPLATE.format(
            args=(
                param_separator + param_separator.join(
                    a.generate()
                    for a in self._args
                )
                if self._args else
                ""
            ),
            indent=indentation_str * indentation,
            fields=(
                "\n".join(a.to_field().generate(indentation + 1, indentation_str) for a in self._args)
                if self._args else
                NO_OP.generate(indentation + 1, indentation_str)
            ),
            comments=_Comments(*[a.to_field_comment() for a in self._args]).generate(indentation + 1, indentation_str)
        )


class _Comments(CodePart):
    TEMPLATE = '''
{indent}"""
{args}
{indent}"""\
'''

    def __init__(self, *args: FieldComment):
        self._args = args

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            args="\n".join(a.generate(indentation, indentation_str) for a in self._args if a.has_comment),
            indent=indentation_str * indentation
        ) if any(a.has_comment for a in self._args) else ""


class _MessageImplementation(CodePart):
    TEMPLATE = """\
{indent}# region <<<Message Implementation>>>
{indent}def __eq__(self, other_msg: '{class_path}') -> bool: ...
{indent}def __str__(self) -> str: ...
{indent}def __unicode__(self) -> str: ...
{indent}def MergeFrom(self, other_msg: '{class_path}'): ...
{indent}def Clear(self): ...
{indent}def SetInParent(self): ...
{indent}def IsInitialized(self) -> bool: ...
{indent}def MergeFromString(self, serialized: str): ...
{indent}def SerializeToString(self, **kwargs) -> str: ...
{indent}def SerializePartialToString(self, **kwargs) -> str: ...
{indent}def ListFields(self) -> List[FieldDescriptor]: ...
{indent}def HasField(self, field_name: str) -> bool: ...
{indent}def ClearField(self, field_name: str): ...
{indent}def WhichOneof(self, oneof_group: str): ...
{indent}def HasExtension(self, extension_handle: str) -> bool: ...
{indent}def ClearExtension(self, extension_handle): ...
{indent}def DiscardUnknownFields(self): ...
{indent}def ByteSize(self) -> int: ...
{indent}def _SetListener(self, message_listener): ...

{indent}# endregion <<<Message Implementation>>>
{indent}...\
"""

    def __init__(self, class_path: str):
        self._class_path = class_path

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            class_path=self._class_path,
            indent=indentation_str * indentation
        )


class Message(CodePart):
    TEMPLATE = """\
{indent}class {class_name}(Message):
{fields}
"""

    def __init__(self, name: str, parents: List[str], *inner: CodePart):
        self._name = name
        self._parent_path = ".".join(parents) + ("." if parents else "")
        self._inner = list(inner)
        self._inner.append(NEW_LINE)
        self._inner.append(_MessageImplementation(self._parent_path + self._name))

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            class_name=self._name,
            parent_path=self._parent_path,
            fields="".join(i.generate(indentation + 1, indentation_str) for i in self._inner),
            indent=indentation_str * indentation
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

    def __contains__(self, item: 'Union[Import, str]'):
        if isinstance(item, Import):
            return item._path == self._path and (
                    not self._from_items or all(i in self._from_items for i in item._from_items))
        elif isinstance(item, str):
            path, name = item.split('.')[1:]
            return path == self._path and (not self._from_items or name in self._from_items)

    # region <<<Comparison operators for sorting>>>
    def __lt__(self, other: 'Import') -> bool:
        return self.generate(0, '') < other.generate(0, '')

    def __gt__(self, other: 'Import') -> bool:
        return self.generate(0, '') > other.generate(0, '')

    def __eq__(self, other: 'Import') -> bool:
        return self.generate(0, '') == other.generate(0, '')

    def __le__(self, other: 'Import') -> bool:
        return self.generate(0, '') <= other.generate(0, '')

    def __ge__(self, other: 'Import') -> bool:
        return self.generate(0, '') >= other.generate(0, '')

    def __ne__(self, other: 'Import') -> bool:
        return self.generate(0, '') != other.generate(0, '')

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
