from stubs_generator.base import FieldType


class SimpleType(FieldType):
    def __init__(self, value_type: str, repeated: bool):
        self._value_type = value_type
        if repeated:
            self._value_type = "List[{}]".format(self._value_type)

    def generate(self) -> str:
        return self._value_type


class MessageType(FieldType):
    def __init__(self, reference: str, repeated: bool):
        self._value_type = reference
        if repeated:
            self._value_type = "List[{}]".format(self._value_type)

    def generate(self) -> str:
        return self._value_type


class OneOfGroupType(FieldType):
    def __init__(self, *fields: FieldType):
        self._value_type = "Union[{}]".format(", ".join(f.generate() for f in fields))

    def generate(self) -> str:
        return self._value_type
