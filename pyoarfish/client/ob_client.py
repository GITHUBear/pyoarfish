"""OceanBase Client."""

import logging
from typing import List, Optional
from sqlalchemy import create_engine, MetaData, Table, Column, Index
from .index_param import IndexParams
from ..schema import VECTOR, ObTable, VectorIndex, CreateVectorIndex

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ObClient:
    """The OceanBase Client"""

    def __init__(
        self,
        uri: str = "127.0.0.1:2881",
        user: str = "root@test",
        password: str = "",
        db_name: str = "test",
        **kwargs,
    ):
        """
        """
        from sqlalchemy.dialects.mysql.base import ischema_names
        ischema_names['VECTOR'] = VECTOR
        connection_str = f"mysql+pymysql://{user}:{password}@{uri}/{db_name}?charset=utf8mb4"
        self.engine = create_engine(connection_str, **kwargs)
        self.metadata_obj = MetaData()
    
    def create_table(
        self,
        table_name: str,
        columns: List[Column],
        indexes: Optional[List[Index]] = None,
    ):
        with self.engine.connect():
            if indexes is not None:
                table = ObTable(
                    table_name,
                    self.metadata_obj,
                    *columns,
                    *indexes
                )
            else:
                table = ObTable(
                    table_name,
                    self.metadata_obj,
                    *columns
                )
            table.create(self.engine, checkfirst=True)

    def create_index(
        self,
        table_name: str,
        is_vec_index: bool,
        index_name: str,
        *column_names: str,
        vidx_params: Optional[str] = None,
        **kw
    ):
        table = Table(table_name, self.metadata_obj, autoload=True, autoload_with=self.engine)
        columns = [table.c[column_name] for column_name in column_names]
        with self.engine.connect():
            if is_vec_index:
                vidx = VectorIndex(index_name, *columns, params=vidx_params, **kw)
                vidx.create(self.engine, checkfirst=True)
            else:
                idx = Index(index_name, *columns, **kw)
                idx.create(self.engine, checkfirst=True)