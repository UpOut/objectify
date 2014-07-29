# coding: utf-8

from .base import ObjectifyProperty

from .boolean import Boolean
from .number import Integer,Float,Long
from .string import Unicode, String

class Dynamic(ObjectifyProperty):
    
    def _check_int_long(self,frm):
        _long = None
        try:
            _long = long(frm)
        except:
            pass

        _int = None
        try:
            _int = int(frm)
        except:
            pass

        if _int is None and _long is None:
            return None

        if _long is None:
            return _int
        elif _int is None:
            return _long

        if _int == _long:
            return _int
        else:
            return _long

    def _check_int_float(self,frm):
        _float = None
        try:
            _float = float(frm)
        except:
            pass

        _int = None
        try:
            _int = int(frm)
        except:
            pass

        if _int is None and _float is None:
            return None

        if _float is None:
            return self._check_int_long(frm)
        elif _int is None:
            return _float

        if _int == _float:
            return self._check_int_long(frm)
        else:
            return _float




    def _to_type(self,frm):

        if isinstance(frm,ObjectifyProperty):
            self.__class__ = frm.__class__
            return frm.from_collection()

        if type(frm) == bool:
            self.__class__ = Boolean
            return frm
        
        typed = self._check_int_float(frm)
        if typed is not None:
            if type(typed) == int:
                self.__class__ = Integer
            elif type(typed) == float:
                self.__class__ = Float
            elif type(typed) == long:
                self.__class__ = Long

            return typed

        try:
            frm = unicode(frm)
            self.__class__ = Unicode
            return frm
        except:
            pass

        try:
            frm = str(frm)
            self.__class__ = String
            return frm
        except:
            pass

        raise RuntimeError("Unable to determine type of value %s" % (frm))





        



        