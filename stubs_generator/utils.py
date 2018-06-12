from itertools import chain
from typing import List, Union, Dict, Iterable

from google.protobuf.descriptor import FieldDescriptor

from stubs_generator.base import CodePart, FieldType
from stubs_generator.fields import MessageType, OneOfGroupType, SimpleType
from stubs_generator.messages import Import


def after_every(items: List[CodePart], *parts: CodePart) -> List[CodePart]:
    """Inserts after every part a list of items"""
    return list(chain(*[[p, *items] for p in parts]))


def before_every(items: List[CodePart], *parts: CodePart) -> List[CodePart]:
    """Inserts before every part a list of items"""
    return list(chain(*[[*items, p] for p in parts]))


def after_if_not_empty(items: List[CodePart], *parts: CodePart, _else: List[CodePart] = list()) -> List[CodePart]:
    """Inserts after all parts a list of items if there are any parts"""
    return [*parts, *items] if parts else _else


def before_if_not_empty(items: List[CodePart], *parts: CodePart, _else: List[CodePart] = list()) -> List[CodePart]:
    """Inserts before all parts a list of items if there are any parts"""
    return [*items, *parts] if parts else _else


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


def get_comments(pf) -> Dict[str, List[str]]:
    """Retrieves comments from proto file and creates a dictionary symbol which comment was aimed at"""
    def _get_inner():
        for location in pf.source_code_info.location:
            if location.trailing_comments or location.leading_comments:
                pf_p = pf
                cls_path = []
                for path in location.path:
                    try:
                        if hasattr(pf_p, "field") or hasattr(pf_p, "method"):
                            cls_path.append(pf_p.name)
                        pf_p = (
                            list(pf_p)[path]
                            if isinstance(pf_p, Iterable) else
                            getattr(pf_p, pf_p.DESCRIPTOR.fields_by_number[path].name)
                        )
                    except AttributeError as ex:
                        raise Exception(pf_p, path) from ex

                # cls_path - parent object names, pf_p - message from decoder
                # location.trailing_comments - at the end of the line
                # location.leading_comments - after commented item
                if location.trailing_comments:
                    yield ".".join(cls_path + [pf_p.name]), [location.trailing_comments.splitlines()[0]]
                else:
                    yield ".".join(cls_path + [pf_p.name]), location.leading_comments.splitlines()

    return dict()
    # return dict(_get_inner())
