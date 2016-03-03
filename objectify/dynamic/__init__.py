# coding: utf-8

from ..prop.base import ObjectifyProperty

from ..prop.boolean import Boolean
from ..prop.number import Integer,Float,Long
from ..prop.string import Unicode, String

from ..model.dict import ObjectifyDict
from ..model.list import ObjectifyList

__all__ = ['DynamicProperty','DynamicList','DynamicDict']

class DynamicProperty(ObjectifyProperty):
    """ Takes in any value and tries to type fit it
        into the proper type / object

        May or may not try to convert strings into numbers
    """

    #Charset for unicode encoding
    __unicode_charset__ = 'utf-8'

    #Whether or not to type fit strings which might be int/long/float
    __type_fit_numbers__ = True

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


        
        if isinstance(frm,dict):
            if not self.__fetch_object__:
                self.__fetch_object__ = _DynamicDictForProperty()

            self.can_fetch_default = True
            self.auto_fetch_default = True
            self.auto_fetch = True

            return frm

        if isinstance(frm,list):
            if not self.__fetch_object__:
                self.__fetch_object__ = _DynamicListForProperty()
            
            self.can_fetch_default = True
            self.auto_fetch_default = True
            self.auto_fetch = True

            return frm
        


        if type(frm) == bool:
            self.__class__ = Boolean
            return frm

        #This will always dynamically shift strings to int/long/float
        if (self.__type_fit_numbers__ or 
                isinstance(frm, int) or
                isinstance(frm, float) or 
                isinstance(frm, long)):
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
            if not isinstance(frm, unicode):
                frm = unicode(frm, self.__unicode_charset__)

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


        raise RuntimeError("Unable to determine type of value %s" % frm)



#Shhh!!! It's weird, but we have to avoid circular references!
class DynamicDict(ObjectifyDict):
    """ Takes in any dictionary and tries to type fit it
        into the proper type / object

        May or may not try to convert strings into numbers
    """

    __dynamic_class__ = DynamicProperty()
    __allow_classed_dynamics__ = True

class DynamicList(ObjectifyList):
    """ Takes in any list and tries to type fit it
        into the proper type / object

        May or may not try to convert strings into numbers
    """

    __list_object__ = DynamicProperty()

class _DynamicDictForProperty(DynamicDict):
    
    def fetch_from(self,frm):
        return self.from_collection(frm,clear=True)

class _DynamicListForProperty(DynamicList):
    
    def fetch_from(self,frm):
        return self.from_collection(frm,clear=True)

