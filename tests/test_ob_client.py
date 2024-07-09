import unittest
from pyoarfish.client import ObClient, VecIndexType, VecIndexParam
from pyoarfish.schema import VECTOR, VectorIndex
from sqlalchemy import Column, Integer, Table
from sqlalchemy.sql import func
from sqlalchemy.exc import NoSuchTableError

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
        idxs = [
            VectorIndex('idx1', 'c2', params='distance=l2, type=hnsw, lib=vsag'),
        ]
        self.client.create_table('ttt', cols, idxs)

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

    def test_precise_search(self):
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

        res = self.client.precise_search('ttt', [0,0,0], 'c2', func.l2_distance, 1, ['c1'])
        print(f"res1 = {res.fetchall()}")
        res = self.client.precise_search('ttt', [0,0,0], 'c2', func.l2_distance, 1)
        print(f"res2 = {res.fetchall()}")

        self.client.drop_table_if_exist('ttt')

    def test_perform_delete(self):
        self.client.drop_table_if_exist('ttt')
        cols = [
            Column('c1', Integer, primary_key=True, autoincrement=False),
            Column('c2', VECTOR(3)),
        ]
        self.client.create_table('ttt', cols)

        data = [
            {'c1':1, 'c2':[1,1,1]},
            {'c1':2, 'c2':[2,2,2]},
            {'c1':3, 'c2':[3,3,3]}
        ]
        self.client.insert('ttt', data)
        
        # customize where clause
        try:
            table = Table('ttt', self.client.metadata_obj, autoload_with=self.client.engine)
        except NoSuchTableError:
            return
        cond = [
            (table.c['c1'] == 1) | (table.c['c1'] == 2)
        ]
        self.client.delete('ttt', cond)

        self.client.drop_table_if_exist('ttt')

    def test_perform_update(self):
        self.client.drop_table_if_exist('ttt')
        cols = [
            Column('c1', Integer),
            Column('c2', VECTOR(3)),
            Column('c3', Integer)
        ]
        self.client.create_table('ttt', cols)

        data = [
            {'c1':1, 'c2':[1,1,1], 'c3':1},
            {'c1':2, 'c2':[2,2,2], 'c3':1},
            {'c1':3, 'c2':[3,3,3], 'c3':1}
        ]
        self.client.insert('ttt', data)

        value_clause = [
            {'c2':[1,2,3]} | {'c3':2}
        ]
        self.client.update('ttt', value_clause)

        self.client.drop_table_if_exist('ttt')

    def test_check_table_exist(self):
        self.client.drop_table_if_exist('ttt')
        self.assertFalse(self.client.check_table_exists('ttt'))

        cols = [
            Column('c1', Integer),
            Column('c2', VECTOR(3)),
            Column('c3', Integer)
        ]
        self.client.create_table('ttt', cols)
        self.assertTrue(self.client.check_table_exists('ttt'))

        self.client.drop_table_if_exist('ttt')
        self.assertFalse(self.client.check_table_exists('ttt'))

if __name__ == '__main__':
    unittest.main()