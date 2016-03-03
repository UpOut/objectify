# coding: utf-8

from .base import ObjectifyProperty

#### PURE STRING ####
class String(ObjectifyProperty):
    """ An ASCII string """
    
    to_type=str

class Str(String):
    pass

class TrimmedString(String):
    """ An ASCII string with whitespace padding removed """

    def _to_type(self,value):
        value = super(TrimmedString, self)._to_type(value)
        return value.strip()



#### UNICODE ####

class Unicode(ObjectifyProperty):
    """ A Unicode (UTF-8) string """

    to_type = unicode
    #Charset for unicode encoding
    __unicode_charset__ = 'utf-8'

    def _to_type(self,value):
        if not isinstance(value, unicode):
            return self.to_type(value,self.__unicode_charset__)
        return value
        

class TrimmedUnicode(Unicode):
    """ A Unicode (UTF-8) string with whitespace padding removed """

    def _to_type(self,value):
        value = super(TrimmedUnicode, self)._to_type(value)

        return value.strip()

