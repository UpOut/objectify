# coding: utf-8

from .prop import ObjectifyProperty
from base import ObjectifyObject

class ObjectifyDictType(type):

    def __new__(cls, name, bases, attrs):
        _attrs = {
            '__obj_attrs__' : {}
        }

        for attr,obj in attrs.iteritems():
            #Check ending first as this is less common
            _attrs[attr] = obj
            if attr[-2:] == "__" and attr[:2] == "__":
                continue

            if isinstance(_attrs[attr],ObjectifyObject):

                _attrs[attr] = _attrs[attr].copy_inited()
                if not getattr(_attrs[attr],"__key_name__",None):
                    _attrs[attr].__key_name__ = attr
                
                if _attrs[attr].__key_name__ in _attrs['__obj_attrs__']:
                    raise RuntimeError("Duplicate key %s" % _attrs[attr].__key_name__)
                _attrs['__obj_attrs__'][_attrs[attr].__key_name__] = attr
        
        return super(ObjectifyDictType, cls).__new__(cls, name, bases, _attrs)

class ObjectifyListType(type):
    pass

