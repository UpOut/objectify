# coding: utf-8

from property import ObjectifyProperty
from base import ObjectifyObject

class ObjectifyDictType(type):

    def __new__(cls, name, bases, attrs):
        attrs['__obj_attrs__'] = {}

        for attr,obj in attrs.iteritems():
            #Check ending first as this is less common
            if attr[-2:] == "__" and attr[:2] == "__":
                continue

            if isinstance(obj,ObjectifyObject):

                attrs[attr] = attrs[attr].duplicate_inited()
                if not getattr(attrs[attr],"name",None):
                    attrs[attr].name = attr
                
                if attrs[attr].name in attrs['__obj_attrs__']:
                    raise RuntimeError("Duplicate key %s" % attrs[attr].name)
                attrs['__obj_attrs__'][attrs[attr].name] = attr

                if attrs[attr].fetch_key:
                    if '__fetch_attr__' in attrs:
                        raise RuntimeError("Object's can only have a single fetch key")

                    attrs['__fetch_attr__'] = attr
        
        return super(ObjectifyDictType, cls).__new__(cls, name, bases, attrs)

class ObjectifyListType(type):
    pass

