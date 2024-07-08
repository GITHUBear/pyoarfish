import unittest
from pyoarfish.client import ObClient
from pyoarfish.schema import VECTOR, VectorIndex
from sqlalchemy import Column, Integer

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


if __name__ == '__main__':
    unittest.main()