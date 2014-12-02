# coding: utf-8

import copy

from .base import ObjectifyProperty

from .boolean import Boolean
from .number import Integer,Float,Long
from .string import Unicode, String

from ..model.base import ObjectifyModel

class Dynamic(ObjectifyProperty):
    
    def _check_int_long(self,frm):
        _long = None
        try:
            _long = long(frm)
        except:
            _long = None

        _int = None
        try:
            _int = int(frm)
        except:
            _int = None

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
            _float = None

        _int = None
        try:
            _int = int(frm)
        except:
            _int = None

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
        """
            You might think we should have a handler along the lines of
            if isinstance(frm,ObjectifyModel):
                ...
            You're right! It just needs to be in the ObjectifyDict class
        """
            
        if isinstance(frm,ObjectifyProperty):
            _fetch = frm.auto_fetch
            _fetch_default = frm.auto_fetch_default
            self.__class__ = frm.__class__
            _frm = frm.to_collection()

            frm.auto_fetch = _fetch
            frm.auto_fetch_default = _fetch_default

            return _frm

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


        



        