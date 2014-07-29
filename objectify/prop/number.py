# coding: utf-8

from .base import ObjectifyProperty

class Integer(ObjectifyProperty):
    to_type=int

class Int(Integer):
    pass

class Float(ObjectifyProperty):
    to_type = float

class Long(ObjectifyProperty):
    to_type = long

