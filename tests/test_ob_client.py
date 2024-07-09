import unittest
from pyoarfish.client import ObClient, VecIndexType, VecIndexParam, VecIndexParams
from pyoarfish.schema import VECTOR, VectorIndex
from sqlalchemy import Column, Integer
from sqlalchemy.sql import func

class ObClientTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = ObClient(echo=True)

    def test_create_vtb_obclient(self):
        cols = [
            Column('c1', Integer, primary_key=True),
            Column('c2', VECTOR(3)),
        ]
        idxs = [
            VectorIndex('idx1', 'c2', params='distance=l2, type=hnsw, lib=vsag'),
        ]
        self.client.create_table('t1', cols, idxs)

    def test_create_vidx_obclient(self):
        cols = [
            Column('c1', Integer, primary_key=True),
            Column('c2', VECTOR(3)),
        ]
        self.client.create_table('t2', cols)
        self.client.create_index('t2', True, 'idx2', 'c2', 
                                 vidx_params='distance=l2, type=hnsw, lib=vsag')

    def test_create_table_with_index_params(self):
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
        self.client.create_table_with_index_params('ttt', cols, None, index_params)

    def test_create_vidx_with_vec_index_param(self):
        cols = [
            Column('c1', Integer, primary_key=True),
            Column('c2', VECTOR(3)),
        ]
        self.client.create_table('ttt', cols)
        vidx_param = VecIndexParam(
            index_name='vidx', 
            field_name='c2', 
            index_type=VecIndexType.HNSW,
            distance='l2',
            lib='vsag',
        )
        self.client.create_vidx_with_vec_index_param('ttt', vidx_param)

    def test_drop_table(self):
        cols = [
            Column('c1', Integer, primary_key=True),
            Column('c2', VECTOR(3)),
        ]
        self.client.create_table('ttt', cols)
        self.client.drop_table_if_exist('ttt')

    def test_insert_data(self):
        self.client.drop_table_if_exist('ttt')
        cols = [
            Column('c1', Integer, primary_key=True, autoincrement=False),
            Column('c2', VECTOR(3)),
        ]
        self.client.create_table('ttt', cols)

        data = [
            {'c1':1, 'c2':[1,1,1]},
            {'c1':2, 'c2':[2,2,2]}
        ]
        self.client.insert('ttt', data)

        self.client.drop_table_if_exist('ttt')

    def test_ann_search(self):
        self.client.drop_table_if_exist('ttt')
        cols = [
            Column('c1', Integer, primary_key=True, autoincrement=False),
            Column('c2', VECTOR(3)),
        ]
        self.client.create_table('ttt', cols)

        data = [
            {'c1':1, 'c2':[1,1,1]},
            {'c1':2, 'c2':[2,2,2]}
        ]
        self.client.insert('ttt', data)

        res = self.client.ann_search('ttt', [0,0,0], 'c2', func.l2_distance, 1, ['c1'])
        print(f"res1 = {res.fetchall()}")
        res = self.client.ann_search('ttt', [0,0,0], 'c2', func.l2_distance, 1)
        print(f"res2 = {res.fetchall()}")

        self.client.drop_table_if_exist('ttt')

if __name__ == '__main__':
    unittest.main()