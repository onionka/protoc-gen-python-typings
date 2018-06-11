from typing import List, Union

from google.protobuf.descriptor import FieldDescriptor

from stubs_generator.base import CodePart, FieldType
from stubs_generator.fields import MessageType, OneOfGroupType, SimpleType
from stubs_generator.messages import Import


def before_every(items: List[CodePart], *parts: CodePart) -> List[CodePart]:
    """Inserts before every part a list of items"""

    def _before_inner():
        for a in parts:
            for i in items:
                yield i
            yield a

    return list(_before_inner())


def before_if_not_empty(items: List[CodePart], *parts: CodePart) -> List[CodePart]:
    """Inserts before parts a list of items if there are any parts"""
    return [*items, *parts] if parts else []


GRPC_TYPE_TO_PYTHON_TYPE = {
    FieldDescriptor.TYPE_DOUBLE: 'float',
    FieldDescriptor.TYPE_FLOAT: 'float',
    FieldDescriptor.TYPE_INT64: 'int',
    FieldDescriptor.TYPE_UINT64: 'int',
    FieldDescriptor.TYPE_INT32: 'int',
    FieldDescriptor.TYPE_FIXED64: 'float',
    FieldDescriptor.TYPE_FIXED32: 'float',
    FieldDescriptor.TYPE_BOOL: 'bool',
    FieldDescriptor.TYPE_STRING: 'str',
    FieldDescriptor.TYPE_BYTES: 'bytes',
    FieldDescriptor.TYPE_UINT32: 'int',
    FieldDescriptor.TYPE_ENUM: 'int',
    FieldDescriptor.TYPE_SFIXED32: 'float',
    FieldDescriptor.TYPE_SFIXED64: 'float',
    FieldDescriptor.TYPE_SINT32: 'int',
    FieldDescriptor.TYPE_SINT64: 'int',
    FieldDescriptor.TYPE_GROUP: 'Group',
    FieldDescriptor.TYPE_MESSAGE: 'Message',
}


class ImportPool(CodePart):
    TEMPLATE = """{imports}"""

    def __init__(self):
        self._imports: List[Import] = []

    def add(self, _im: Import):
        if _im not in self:
            self._imports.append(_im)

    def __contains__(self, item: Union[Import, str]) -> bool:
        return any(item in im for im in self._imports)

    def generate(self, indentation: int, indentation_str: str) -> str:
        return self.TEMPLATE.format(
            imports="".join([im.generate(indentation, indentation_str)
                             for im in sorted(self._imports)]),
        )


def decode_type(type: int = FieldDescriptor.TYPE_MESSAGE, name: str = None, repeated: bool = False,
                import_pool: ImportPool = None, proto_name: str = "", parents: List[str] = None) -> FieldType:
    """Decodes a type of field and creates appropriate descriptor for it"""
    if type == FieldDescriptor.TYPE_MESSAGE:
        assert name is not None
        if import_pool:
            *import_path, cls_name = name.split(".")[1:]
            if not parents or ".".join(import_path) not in ".".join(parents):
                if repeated:
                    import_pool.add(Import("typing", ["List"]))
                if not import_path:
                    import_path = "{}_pb2".format(proto_name).split('/')
                import_pool.add(Import(".".join(import_path), ['*']))
                return MessageType(cls_name, repeated=repeated)
        return MessageType(name.split(".")[-1], repeated=repeated)
    if type == FieldDescriptor.TYPE_GROUP:
        return OneOfGroupType()  # FIXME: TYPE_GROUP was not used in oneof construction
    try:
        return SimpleType(GRPC_TYPE_TO_PYTHON_TYPE[type], repeated=repeated)
    except Exception as ex:
        raise Exception(str(type)) from ex
