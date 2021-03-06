# coding: utf-8

from decimal import Decimal as python_Decimal
from decimal import getcontext, localcontext, setcontext

from .base import ObjectifyProperty


class Integer(ObjectifyProperty):
    """ A system dependent (32 or 64 bit) integer """

    to_type=int

    
    def example_value(self):
        return 1234

class Int(Integer):
    pass

class Float(ObjectifyProperty):
    """ A float """

    to_type = float

    
    def example_value(self):
        return 12.34

class Long(ObjectifyProperty):
    """ A 64 bit integer """

    to_type = long

    
    def example_value(self):
        return 12345678910111213141516L

class Decimal(ObjectifyProperty):
    """ A Python decimal, attempts exact precision
    
        Rounding, precision, etc. may vary depending on use 
    """

    to_type = python_Decimal

    __decimal_context_kwargs__ = {}

    __decimal_context_keys__ = frozenset([
        'prec',
        'rounding',
        'traps',
        'flags',
        'Emin',
        'Emax',
        'capitals'
    ])

    __decimal_use_local_context__ = True

    __decimal_local_context_class__ = None

    def _set_ctx_vars(self,ctx):
        for k in self.__decimal_context_keys__:
            if k in self.__decimal_context_kwargs__:
                setattr(
                    ctx,
                    k,
                    self.__decimal_context_kwargs__[k]
                )

    def _to_type(self,value):

        if self.__decimal_use_local_context__:
            
            with localcontext(self.__decimal_local_context_class__) as ctx:
                self._set_ctx_vars(ctx)
                value = self.to_type(
                    value,
                    ctx
                )
        else:
            ctx = getcontext()
            self._set_ctx_vars(ctx)
            value = self.to_type(
                value,
                ctx
            )

            setcontext(ctx)

        return value

    
    def example_value(self):
        return python_Decimal("12.34")


