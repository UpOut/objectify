# coding: utf-8

from .base import ObjectifyModel
from ..base import ObjectifyObject
from ..meta import ObjectifyListType

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

        from ..dynamic import DynamicProperty
        if isinstance(self.__list_object__, DynamicProperty):
            return self.__morph_dynamic_item__(item)

        if not isinstance(item,self.__list_object__.__class__):

            _item = self.__list_object__.copy_inited()
            
            _item.from_collection(item)
        else:
            _item = item

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

            from ..dynamic import DynamicDict
            _item = DynamicDict()
            _item.from_collection(item)
        
            return _item

        if isinstance(item,list):
            """
                In this case we need to create a DynamicList object to properly fit our data
            """
            from ..dynamic import DynamicList
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

    def __iter__(self,raw=False):
        i = 0
        while i < len(self):
            yield self.__getitem__(i,raw=raw)
            i += 1

    def __raw_iter__(self):
        #We also want to bypass our overload
        return super(ObjectifyList, self).__iter__()

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

    def empty(self):
        return not bool(self)


    def verify_exclude(self,exclude):
        #Raise an exception if we get an empty value

        for ex in exclude:
            if not ex:
                raise RuntimeError("Empty area in exclude path %s in %s" % (exclude,self.__repr__()))


    def split_exclude(self,exclude):

        passdown = set()
        for ex in exclude:
            ex_l = ex.split(".")
            self.verify_exclude(ex_l)

            if len(ex_l) < 2:
                raise RuntimeError("Unable to handle ending exclude path in ObjectifyList %s!" % self.__repr__())

            if ex_l[0] != "[0]":
                raise RuntimeError("Exclude path touches ObjectifyList without [0]!")

            passdown.add(".".join(ex_l[1:]))

        return passdown

    def to_collection(self,exclude=None):
        to_return = []
        
        passdown_exclude = None
        if exclude:
            passdown_exclude = self.split_exclude(exclude)

        for obj in self.__raw_iter__():
            if passdown_exclude:
                to_return.append(obj.to_collection(
                    exclude=passdown_exclude
                ))
            else:
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

    def example_value(self):
        return [self.__list_object__.example_value()]
