from typing import List
from enum import Enum

class IndexType(Enum):
    HNSW = 0
    IVFFLAT = 1

class IndexParam:
    def __init__(self, index_name: str, field_names: List[str], index_type: IndexType, **kwargs):
        self.index_name = index_name
        self.field_names = field_names
        self.index_type = index_type
        self.kwargs = kwargs

    @property
    def field_names(self):
        return self.field_names

    @property
    def index_name(self):
        return self.index_name

    @property
    def index_type(self):
        return self.index_type

    def __iter__(self):
        yield "field_name", self.field_name
        if self.index_type:
            yield "index_type", self.index_type
        yield "index_name", self.index_name
        yield from self._kwargs.items()

    def __str__(self):
        return str(dict(self))

    def __eq__(self, other: None):
        if isinstance(other, self.__class__):
            return dict(self) == dict(other)

        if isinstance(other, dict):
            return dict(self) == other
        return False
    
class IndexParams:
    pass