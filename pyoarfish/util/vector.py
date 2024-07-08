import numpy as np

class Vector:
    def __init__(self, value):
        # big-endian float32
        if not isinstance(value, np.ndarray) or value.dtype != '>f4':
            value = np.asarray(value, dtype='>f4')

        if value.ndim != 1:
            raise ValueError('expected ndim to be 1')

        self._value = value

    def __repr__(self):
        return f'{self._value.tolist()}'
    
    def dim(self):
        return len(self._value)
    
    def to_list(self):
        return self._value.tolist()
    
    def to_numpy(self):
        return self._value
    
    def to_text(self):
        return '[' + ','.join([str(float(v)) for v in self._value]) + ']'
    
    @classmethod
    def from_text(cls, value: str):
        return cls([float(v) for v in value[1:-1].split(',')])
    
    @classmethod
    def _to_db(cls, value, dim=None):
        if value is None:
            return value

        if not isinstance(value, cls):
            value = cls(value)

        if dim is not None and value.dim() != dim:
            raise ValueError('expected %d dimensions, not %d' % (dim, value.dim()))

        return value.to_text()
    
    @classmethod
    def _from_db(cls, value):
        if value is None or isinstance(value, np.ndarray):
            return value

        return cls.from_text(value).to_numpy().astype(np.float32)
