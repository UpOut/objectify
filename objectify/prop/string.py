# coding: utf-8

from .base import ObjectifyProperty

class String(ObjectifyProperty):
    to_type=str

class Str(String):
    pass

class Unicode(ObjectifyProperty):
    to_type = unicode

class TrimmedString(ObjectifyProperty):
    to_type = str

    def _to_type(self,value):
        value = super(TrimmedString, self)._to_type(value)

        return value.strip()

class TrimmedUnicode(ObjectifyProperty):
    to_type = unicode

    def _to_type(self,value):
        value = super(TrimmedUnicode, self)._to_type(value)

        return value.strip()

