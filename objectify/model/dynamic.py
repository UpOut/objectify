# coding: utf-8


from .dict import ObjectifyDict
from .list import ObjectifyList

from ..prop import Dynamic

class DynamicDict(ObjectifyDict):
    __dynamic_class__ = Dynamic()
    __allow_classed_dynamics__ = True

class DynamicList(ObjectifyList):
    __list_object__ = Dynamic()