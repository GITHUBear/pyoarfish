from sqlalchemy import Table
from .vector_index import ObSchemaGenerator

class ObTable(Table):
    def create(self, bind, checkfirst: bool = False) -> None:
        bind._run_ddl_visitor(ObSchemaGenerator, self, checkfirst=checkfirst)