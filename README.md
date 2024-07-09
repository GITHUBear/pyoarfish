# pyoarfish

A python binding library for OceanBase Vector Store.

## quick start

- Create a table with vector column.

```python
from pyoarfish.client import ObClient
from pyoarfish.schema import VECTOR
from sqlalchemy import Column, Integer

client = ObClient(echo=True)
cols = [
    Column('c1', Integer, primary_key=True),
    Column('c2', VECTOR(3)),
]
client.create_table('t1', cols)
```

- Create a table with vector index and common index.

```python
from pyoarfish.client import ObClient
from pyoarfish.schema import VECTOR, VectorIndex
from sqlalchemy import Column, Integer, Index

client = ObClient(echo=True)
cols = [
    Column('c1', Integer),
    Column('c2', VECTOR(3)),
]
idxs = [
    Index('idx1', 'c1'),
    VectorIndex('idx1', 'c2', params='distance=l2, type=hnsw, lib=vsag'),
]
client.create_table('t1', cols, idxs)
```

- Create a table with vector index and common index by `VectorIndexParams`.

```python
from pyoarfish.client import ObClient
from pyoarfish.schema import VECTOR
from sqlalchemy import Column, Integer, Index

client = ObClient(echo=True)
cols = [
    Column('c1', Integer, primary_key=True),
    Column('c2', VECTOR(3)),
]
index_params = self.client.prepare_index_params()
index_params.add_index(
    field_name='c2',
    index_type=VecIndexType.HNSW,
    index_name='vidx',
    distance='l2',
    lib='vsag',
)
# more index_params.add_index...
client.create_table_with_index_params('ttt', cols, None, index_params)
```

- Create Vector Index by `VecIndexParam` after table is created.

```python
from pyoarfish.client import ObClient, VecIndexParam
from pyoarfish.schema import VECTOR
from sqlalchemy import Column, Integer

client = ObClient(echo=True)
cols = [
    Column('c1', Integer, primary_key=True),
    Column('c2', VECTOR(3)),
]
client.create_table('ttt', cols)

vidx_param = VecIndexParam(
    index_name='vidx', 
    field_name='c2', 
    index_type=VecIndexType.HNSW,
    distance='l2',
    lib='vsag',
)
client.create_vidx_with_vec_index_param('ttt', vidx_param)
```

- Do ANN search & Precise search

```python
from pyoarfish.client import ObClient
from pyoarfish.schema import VECTOR, VectorIndex
from sqlalchemy import Column, Integer

client = ObClient(echo=True)
# drop table
client.drop_table_if_exist('ttt')

# create table
cols = [
    Column('c1', Integer, primary_key=True, autoincrement=False),
    Column('c2', VECTOR(3)),
]
idxs = [
    VectorIndex('idx1', 'c2', params='distance=l2, type=hnsw, lib=vsag'),
]
client.create_table('ttt', cols, idxs)

# insert data
data = [
    {'c1':1, 'c2':[1,1,1]},
    {'c1':2, 'c2':[2,2,2]}
]
client.insert('ttt', data)

# do ANN search
res = client.ann_search('ttt', [0,0,0], 'c2', func.l2_distance, 1, ['c1'])
print(f"res1 = {res.fetchall()}")
# do Precise search
res = self.client.precise_search('ttt', [0,0,0], 'c2', func.l2_distance, 1)
print(f"res2 = {res.fetchall()}")

client.drop_table_if_exist('ttt')
```

- more examples...