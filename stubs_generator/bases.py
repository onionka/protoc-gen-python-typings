from abc import abstractmethod, ABC


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
