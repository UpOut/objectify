# coding: utf-8

from .base import ObjectifyModel
from ..base import ObjectifyObject
from ..meta import ObjectifyListType
from ..prop import Dynamic

class ObjectifyList(ObjectifyModel,list):
    __metaclass__ = ObjectifyListType
    """
        The instantiated ObjectifyObject class we want to use in our list
    """
    __list_object__ = None

    def __init__(self,list_object=None,**kwargs):
        self.__fetch_attr__ = None
        
        if list_object is not None:
            self.__list_object__ = list_object

        if self.__list_object__ is None:
            raise RuntimeError("Cannot have an ObjectifyList without a __list_object__")

        super(ObjectifyList, self).__init__(list_object=list_object, **kwargs)


    def __morph_item__(self,item):
        """
            Morph an item to insert it into the list
        """

        if isinstance(self.__list_object__, Dynamic):
            return self.__morph_dynamic_item__(item)

        if isinstance(item,self.__list_object__.__class__):
            item = item.to_collection()

        _item = self.__list_object__.copy_inited()
        
        _item.from_collection(item)

        return _item

    def __morph_dynamic_item__(self,item):
        """
            This function handles morphing items when the __list_object__ is an instance of objectify.prop.Dynamic
        """

        if isinstance(item,ObjectifyModel):
            """
                A dynamic attribute simply wants to adapt any value to the closest ObjectifyObject representation
                In this case we already have a best fit, which is the raw value
            """

            return item

        """
            This function handles setting attributes which are or subclass
            our Dynamic property
        """

        if isinstance(item,dict):
            """
                In this case we need to create a DynamicDict object to properly fit our data
            """

            from .dynamic import DynamicDict
            _item = DynamicDict()
            _item.from_collection(item)
        
            return _item

        if isinstance(item,list):
            """
                In this case we need to create a DynamicList object to properly fit our data
            """
            from .dynamic import DynamicList
            _item = DynamicList()
            _item.from_collection(item)

            return _item
        

        _item = self.__list_object__.copy_inited()
        _item.from_collection(item)
        return _item


    def __setitem__(self, key, item):
        _item = self.__morph_item__(item)
        super(ObjectifyList, self).__setitem__(key,_item)

    def __getitem__(self, key, raw=False):
        existing = super(ObjectifyList, self).__getitem__(key)
        if not raw:
            if isinstance(existing,ObjectifyObject) and not isinstance(existing,ObjectifyModel):
                return existing.to_collection()
        
        return existing

    def append(self,item):
        _item = self.__morph_item__(item)
        super(ObjectifyList, self).append(_item)

    def extend(self,item):
        _item = self.__morph_item__(item)
        super(ObjectifyList, self).extend(_item)

    def insert(self,key,item):
        _item = self.__morph_item__(item)
        super(ObjectifyList, self).insert(key,_item)

    def get_raw_item(self,key):
        return self.__getitem__(key,raw=True)

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
            self.append(self.__morph_item__(obj))

    def copy_inited(self,keep_name=True):
        if keep_name:
            self.__init_kwargs__['name'] = self.__key_name__

        cl = self.__class__(
            *self.__init_args__,
            **self.__init_kwargs__
        )

        cl.__list_object__ = cl.__list_object__.copy_inited()
        
        return cl