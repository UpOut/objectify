# coding: utf-8

from .base import ObjectifyModel
from ..meta import ObjectifyListType

class ObjectifyList(ObjectifyModel,list):
    __metaclass__ = ObjectifyListType
    """
        The instantiated ObjectifyObject class we want to use in our list
    """
    __list_object__ = None

    def __init__(self,list_object=None,**kwargs):
        super(ObjectifyList, self).__init__(list_object=list_object, **kwargs)

        if list_object is not None:
            self.__list_object__ = list_object

        if self.__list_object__ is None:
            raise RuntimeError("Cannot have an ObjectifyList without a __list_object__")

    def __setitem__(self, key, item):
        if isinstance(item,self.__list_object__.__class__):
            item = item.to_collection()

        self[key] = self.__list_object__.duplicate_inited()
        self[key].from_collection(item)

    def to_collection(self):
        to_return = []
        for obj in self:
            to_return.append(obj.to_collection())

        return to_return

    def from_collection(self,lst,clear=True):
        if clear:
            del self[:]
        
        if not isinstance(lst,list):
            lst = [lst]

        for obj in lst:
            if not isinstance(obj,self.__list_object__.__class__):
                _obj = obj
                obj = self.__list_object__.duplicate_inited()
                obj.from_collection(_obj)

            self.append(obj)

    def duplicate_inited(self,keep_name=True):
        if keep_name:
            self.__init_kwargs__['name'] = self.name

        cl = self.__class__(
            *self.__init_args__,
            **self.__init_kwargs__
        )

        cl.__list_object__ = cl.__list_object__.duplicate_inited()
        
        return cl