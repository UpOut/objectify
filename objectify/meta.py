# coding: utf-8

from .prop import ObjectifyProperty
from base import ObjectifyObject

class ObjectifyDictType(type):

    def __new__(cls, name, bases, attrs):
        _attrs = {
            '__obj_attrs__' : {},
            '__passdown_attributes__' : {}
        }

        _parent_attributes = set()
        for base in bases:
            _obj_attrs = None
            try:
                _obj_attrs = base.__obj_attrs__
            except:
                pass

            if _obj_attrs:
                _attrs['__obj_attrs__'] = dict(
                    _attrs['__obj_attrs__'].items() + 
                    _obj_attrs.items()
                )

        for key in _attrs['__obj_attrs__'].keys():
            _parent_attributes.add(key)

        _passdown_check = {}
        for attr,obj in attrs.iteritems():
            #Check ending first as this is less common
            _attrs[attr] = obj
            if attr[-2:] == "__" and attr[:2] == "__":
                continue

            if isinstance(_attrs[attr],ObjectifyObject):
                _attrs[attr] = _attrs[attr].copy_inited()
                if not getattr(_attrs[attr],"__key_name__",None):
                    _attrs[attr].__key_name__ = attr
                
                if (_attrs[attr].__key_name__ in _attrs['__obj_attrs__'] and 
                        _attrs[attr].__key_name__ not in _parent_attributes):
                    raise RuntimeError("Duplicate key %s" % _attrs[attr].__key_name__)

                _attrs['__obj_attrs__'][_attrs[attr].__key_name__] = attr
            
                try:
                    if _attrs[attr].__passdown_from__ is not None:
                        _passdown_check[attr] = _attrs[attr].__passdown_from__
                except AttributeError:
                    pass


        for to_attr,passdown in _passdown_check.iteritems():

            for from_attr,child_attr in passdown.iteritems():

                if from_attr not in _attrs['__passdown_attributes__']:
                    _attrs['__passdown_attributes__'][from_attr] = []

                if isinstance(from_attr,basestring):
                    if from_attr not in _attrs:
                        raise RuntimeError("Cannot find passdown attribute %s in parent object" % (from_attr))

                    from_attr = _attrs[from_attr]


                if not isinstance(from_attr,ObjectifyObject):
                    raise RuntimeError("passdown_from keys MUST be strings")

                if not isinstance(child_attr,basestring):
                    raise RuntimeError("passdown_from values MUST be strings")

                from_attr = from_attr.__key_name__

                _attrs['__passdown_attributes__'][from_attr].append(
                    (to_attr,child_attr)
                )                






        return super(ObjectifyDictType, cls).__new__(cls, name, bases, _attrs)

class ObjectifyListType(type):
    pass

