from typing import List
from enum import Enum

class VecIndexType(Enum):
    HNSW = 0
    IVFFLAT = 1

class VecIndexParam:
    def __init__(self, index_name: str, field_name: str, index_type: VecIndexType, **kwargs):
        self.index_name = index_name
        self.field_name = field_name
        self.index_type = index_type
        self.kwargs = kwargs
    
    def get_vector_index_type_str(self):
        if self.index_type == VecIndexType.HNSW:
            return "hnsw"
        elif self.index_type == VecIndexType.IVFFLAT:
            return "ivfflat"
        else:
            raise ValueError(f"unsupported vector index type: {self.index_type}")
    
    def param_str(self):
        partial_str = ','.join([f'{k}={v}' for k,v in self.kwargs.items()])
        if len(partial_str) > 0:
            partial_str += ','
        partial_str += f'type={self.get_vector_index_type_str()}'
        return partial_str

    def __iter__(self):
        yield "field_name", self.field_name
        if self.index_type:
            yield "index_type", self.index_type
        yield "index_name", self.index_name
        yield from self.kwargs.items()

    def __str__(self):
        return str(dict(self))

    def __eq__(self, other: None):
        if isinstance(other, self.__class__):
            return dict(self) == dict(other)

        if isinstance(other, dict):
            return dict(self) == other
        return False
    
class VecIndexParams:
    def __init__(self):
        self._indexes = {}

    def add_index(self, field_name: str, index_type: VecIndexType, index_name: str = "", **kwargs):
        index_param = VecIndexParam(index_name, field_name, index_type, **kwargs)
        pair_key = (field_name, index_name)
        self._indexes[pair_key] = index_param

    def __iter__(self):
        for v in self._indexes.values():
            yield v

    def __str__(self):
        return str(list(self))