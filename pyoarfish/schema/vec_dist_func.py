from sqlalchemy.sql import func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy import Float

class l2_distance(FunctionElement):
    type = Float()

@compiles(l2_distance)
def compile_l2_distance(element, compiler, **kwargs):
    args = ', '.join(compiler.process(arg) for arg in element.clauses)
    return f'l2_distance({args})'

class cosine_distance(FunctionElement):
    type = Float()

@compiles(cosine_distance)
def compile_cosine_distance(element, compiler, **kwargs):
    args = ', '.join(compiler.process(arg) for arg in element.clauses)
    return f'cosine_distance({args})'

class inner_product(FunctionElement):
    type = Float()

@compiles(inner_product)
def compile_inner_product(element, compiler, **kwargs):
    args = ', '.join(compiler.process(arg) for arg in element.clauses)
    return f'inner_product({args})'