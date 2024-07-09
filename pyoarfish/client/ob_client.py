"""OceanBase Client."""

import logging
from typing import List, Optional, Dict, Union
from sqlalchemy import create_engine, MetaData, Table, Column, Index, select
from sqlalchemy.exc import NoSuchTableError
from .index_param import VecIndexParams, VecIndexParam
from ..schema import VECTOR, ObTable, VectorIndex, CreateVectorIndex, l2_distance, cosine_distance, inner_product

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
        import sqlalchemy.sql.functions as func_mod
        ischema_names['VECTOR'] = VECTOR
        setattr(func_mod, 'l2_distance', l2_distance)
        setattr(func_mod, 'cosine_distance', cosine_distance)
        setattr(func_mod, 'inner_product', inner_product)

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
                    *indexes,
                    extend_existing=True
                )
            else:
                table = ObTable(
                    table_name,
                    self.metadata_obj,
                    *columns,
                    extend_existing=True
                )
            table.create(self.engine, checkfirst=True)
    
    @classmethod
    def prepare_index_params(cls):
        return VecIndexParams()
    
    def create_table_with_index_params(
        self,
        table_name: str,
        columns: List[Column],
        indexes: Optional[List[Index]] = None,
        vidxs: Optional[VecIndexParams] = None,
    ):
        all_idxs = indexes if indexes is not None else []
        if vidxs is not None:
            for vidx_param in vidxs:
                all_idxs.append(
                    VectorIndex(
                        vidx_param.index_name, 
                        vidx_param.field_name, 
                        params=vidx_param.param_str()
                    )
                )
        self.create_table(table_name, columns, all_idxs)

    def create_index(
        self,
        table_name: str,
        is_vec_index: bool,
        index_name: str,
        *column_names: str,
        vidx_params: Optional[str] = None,
        **kw
    ):
        try:
            table = Table(table_name, self.metadata_obj, autoload_with=self.engine)
        except NoSuchTableError:
            return
        columns = [table.c[column_name] for column_name in column_names]
        with self.engine.connect():
            if is_vec_index:
                vidx = VectorIndex(index_name, *columns, params=vidx_params, **kw)
                vidx.create(self.engine, checkfirst=True)
            else:
                idx = Index(index_name, *columns, **kw)
                idx.create(self.engine, checkfirst=True)
    
    def create_vidx_with_vec_index_param(
        self,
        table_name: str,
        vidx_param: VecIndexParam,
    ):
        try:
            table = Table(table_name, self.metadata_obj, autoload_with=self.engine)
        except NoSuchTableError:
            return
        with self.engine.connect():
            vidx = VectorIndex(
                vidx_param.index_name,
                table.c[vidx_param.field_name],
                params=vidx_param.param_str()
            )
            vidx.create(self.engine, checkfirst=True)

    def drop_table_if_exist(self, table_name: str):
        try:
            table = Table(table_name, self.metadata_obj, autoload_with=self.engine)
        except NoSuchTableError:
            return
        with self.engine.connect():
            table.drop(self.engine, checkfirst=True)

    def insert(
        self,
        table_name: str,
        data: Union[Dict, List[Dict]],
    ):
        if isinstance(data, Dict):
            data = [data]

        if len(data) == 0:
            return

        try:
            table = Table(table_name, self.metadata_obj, autoload_with=self.engine)
        except NoSuchTableError:
            return
        
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(table.insert().values(data))

    def upsert(
        self,
        table_name: str,
        data: Union[Dict, List[Dict]],
    ):
        pass

    def ann_search(
        self,
        table_name: str,
        vec_data: list,
        vec_column_name: str,
        distance_func,
        topk: int = 10,
        output_column_name: Optional[List[str]] = None,
    ):
        try:
            table = Table(table_name, self.metadata_obj, autoload_with=self.engine)
        except NoSuchTableError:
            return

        if output_column_name is not None:
            columns = [table.c[column_name] for column_name in output_column_name]
            stmt = select(*columns).order_by(distance_func(table.c[vec_column_name], str(vec_data))).limit(topk)
            with self.engine.connect() as conn:
                with conn.begin():
                    return conn.execute(stmt)
        else:
            stmt = select(table).order_by(distance_func(table.c[vec_column_name], str(vec_data))).limit(topk)
            with self.engine.connect() as conn:
                with conn.begin():
                    return conn.execute(stmt)