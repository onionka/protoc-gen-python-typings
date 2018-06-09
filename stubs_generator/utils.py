from typing import List

from google.protobuf.descriptor import FieldDescriptor

from stubs_generator.bases import CodePart, FieldType
from stubs_generator.fields import MessageType, OneOfGroupType, SimpleType


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


def decode_type(field) -> FieldType:
    """Decodes a type of field and creates appropriate descriptor for it"""
    if field.type == FieldDescriptor.TYPE_MESSAGE:
        return MessageType(field.type_name.split(".")[-1], repeated=field.label == FieldDescriptor.LABEL_REPEATED)
    if field.type == FieldDescriptor.TYPE_GROUP:
        return OneOfGroupType()  # FIXME: TYPE_GROUP was not used in oneof construction
    return SimpleType(GRPC_TYPE_TO_PYTHON_TYPE[field.type], repeated=field.label == FieldDescriptor.LABEL_REPEATED)
