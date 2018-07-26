from typing import List

from .base import CodePart, FieldType, NO_OP


class _Comments(CodePart):
    TEMPLATE = '''\
{indent}"""{comment}"""
'''

    def __init__(self, comments: List[str]):
        self._comments = comments

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            comment=(
                ("\n" + indentation_str * indentation + "   ").join(self._comments)
                + ("\n" + indentation_str * indentation if len(self._comments) > 1 else "")
            ),
            indent=indentation_str * indentation
        )


class StubMethod(CodePart):
    TEMPLATE = """\
{indent}def {name}(self,
{indent}    {name_padding} request: {arg_type},
{indent}    {name_padding} timeout: int = None,
{indent}    {name_padding} metadata: Any = None,
{indent}    {name_padding} credentials: CallCredentials = None
{indent}    {name_padding} ) -> {return_type}:
{comments}\
"""

    def __init__(self, name: str, arg_type: FieldType, return_type: FieldType, comments: List[str] = list()):
        self._name = name
        self._arg_type = arg_type
        self._return_type = return_type
        self._comments = _Comments(comments) if comments else None

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            arg_type=self._arg_type.generate(),
            return_type=self._return_type.generate(),
            indent=indentation_str * indentation,
            comments=(self._comments or NO_OP).generate(indentation + 1, indentation_str),
            name_padding=" " * len(self._name)
        )


class AbstractMethod(CodePart):
    TEMPLATE = """\
{indent}@abstractmethod    
{indent}def {name}(self,
{indent}    {name_padding} request: {arg_type},
{indent}    {name_padding} context: ServicerContext
{indent}    {name_padding} ) -> {return_type}:
{comments}\
"""

    def __init__(self, name: str, arg_type: FieldType, return_type: FieldType, comments: List[str] = list()):
        self._name = name
        self._arg_type = arg_type
        self._return_type = return_type
        self._comments = _Comments(comments) if comments else None

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            arg_type=self._arg_type.generate(),
            return_type=self._return_type.generate(),
            indent=indentation_str * indentation,
            comments=(self._comments or NO_OP).generate(indentation + 1, indentation_str),
            name_padding=" " * len(self._name)
        )


class Stub(CodePart):
    TEMPLATE = """\
{indent}class {name}Stub(object):{comments}
{inner_indent}def __init__(self, channel: Channel):
{inner_indent}{noop}
{methods}\
"""

    def __init__(self, name: str, *method: StubMethod, comments: List[str] = list()):
        self._name = name
        self._meths = list(method)
        self._comments = _Comments(comments) if comments else None

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            methods="\n".join(meth.generate(indentation + 1, indentation_str) for meth in self._meths),
            indent=indentation_str * indentation,
            inner_indent=indentation_str * (indentation + 1),
            noop=NO_OP.generate(1, indentation_str),
            comments=("\n" + self._comments.generate(indentation + 1, indentation_str)) if self._comments else ""
        )


class Servicer(CodePart):
    TEMPLATE = """\
{indent}class {name}Servicer(ABC):{comments}
{methods}\
"""

    def __init__(self, name: str, *method: AbstractMethod, comments: List[str] = list()):
        self._name = name
        self._meths = list(method)
        if not self._meths:
            self._meths = [NO_OP]
        self._comments = _Comments(comments) if comments else None

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            methods="\n".join(meth.generate(indentation + 1, indentation_str) for meth in self._meths),
            indent=indentation_str * indentation,
            comments=("\n" + self._comments.generate(indentation + 1, indentation_str)) if self._comments else ""
        )


class AddToServerMethod(CodePart):
    TEMPLATE = """\
{indent}def add_{name}Servicer_to_server(servicer: {name}Servicer, server: Server):
{indent}{noop}\
"""

    def __init__(self, name: str):
        self._name = name

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            indent=indentation_str * indentation,
            noop=NO_OP.generate(1, indentation_str)
        )
