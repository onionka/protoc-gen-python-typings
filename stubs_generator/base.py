from abc import ABC, abstractmethod
from typing import cast, Type


class FieldType(ABC):
    """Base class for all field type representations in proto file
       with `generate` method that returns its representation in python"""

    @abstractmethod
    def generate(self) -> str:
        pass


class CodePart(ABC):
    """Base class for all construction (message, enum, field, ...) representations in proto file
       with `generate` method that returns its representation in python"""

    @abstractmethod
    def generate(self, indentation: int, indentation_str: str) -> str:
        pass


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
