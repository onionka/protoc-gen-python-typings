from .base import CodePart, FieldType, NO_OP


class StubMethod(CodePart):
    TEMPLATE = """\
{indent}def {name}(self, request: {arg_type}, timeout: int = 0) -> {return_type}:
{indent}{noop}\
"""

    def __init__(self, name: str, arg_type: FieldType, return_type: FieldType):
        self._name = name
        self._arg_type = arg_type
        self._return_type = return_type

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            arg_type=self._arg_type.generate(),
            return_type=self._return_type.generate(),
            indent=indentation_str * indentation,
            noop=NO_OP.generate(1, indentation_str)
        )


class AbstractMethod(CodePart):
    TEMPLATE = """\
{indent}@abstractmethod    
{indent}def {name}(self, request: {arg_type}, context: ServicerContext) -> {return_type}:
{indent}{noop}\
"""

    def __init__(self, name: str, arg_type: FieldType, return_type: FieldType):
        self._name = name
        self._arg_type = arg_type
        self._return_type = return_type

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            arg_type=self._arg_type.generate(),
            return_type=self._return_type.generate(),
            indent=indentation_str * indentation,
            noop=NO_OP.generate(1, indentation_str)
        )


class Stub(CodePart):
    TEMPLATE = """\
{indent}class {name}Stub(object):
{inner_indent}def __init__(self, channel: Channel):
{inner_indent}{noop}
{methods}\
"""

    def __init__(self, name: str, *method: StubMethod):
        self._name = name
        self._meths = list(method)

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            methods="\n".join(meth.generate(indentation + 1, indentation_str) for meth in self._meths),
            indent=indentation_str * indentation,
            inner_indent=indentation_str * (indentation + 1),
            noop=NO_OP.generate(1, indentation_str)
        )


class Servicer(CodePart):
    TEMPLATE = """\
{indent}class {name}Servicer(ABC):
{methods}\
"""

    def __init__(self, name: str, *method: AbstractMethod):
        self._name = name
        self._meths = list(method)
        if not self._meths:
            self._meths = [NO_OP]

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            name=self._name,
            methods="\n".join(meth.generate(indentation + 1, indentation_str) for meth in self._meths),
            indent=indentation_str * indentation
        )


class AddToServerMethod(CodePart):
    TEMPLATE = """\
{indent}def add_{name}Servicer_to_server(servicer: {name}Servicer):
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
