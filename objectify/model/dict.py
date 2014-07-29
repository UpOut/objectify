# coding: utf-8

from .base import ObjectifyModel
from ..base import ObjectifyObject
from ..prop import ObjectifyProperty
from ..meta import ObjectifyDictType

class ObjectifyDict(ObjectifyModel,dict):

    __metaclass__ = ObjectifyDictType



    """
        This allows the dynamic introduction of attributes to the dictionary
        Each of the new attributes will be created using the matching __dynamic_class__
        Should already be instantiated 

        Note: Any existing "name" parameter in the class will be overwritten
    """
    __dynamic_class__ = None



    """
        This allows the introduction of dynamic attributes which are not the same class specified in __dynamic_class__

        Note: Any existing "name" parameter in the class will be overwritten
    """
    __allow_classed_dynamics__ = False



    """
        Attributes which represent values from the object this class represents
        Format:
        {
            "object_attr" : "class_attr"
        }
    """
    __obj_attrs__ = {}



    def __setattr__(self,name,val,raw=False):
        if name[-2:] == "__" and name[:2] == "__":
            return super(ObjectifyDict, self).__setattr__(name,val)
        
        existing = getattr(self,name,None)
        try:
            existing = self.__getattribute__(name,raw=True)
        except Exception as e:
            if self.__dynamic_class__ is not None:
                return self.__setattr_dynamic__(name,val)
            elif self.__allow_classed_dynamics__:
                return self.__setattr_dynamic__(name,val)
            else:
                raise RuntimeError("Introduction of unknown attribute %s disallowed, please use __dynamic_class__ and/or __allow_classed_dynamics__" % (name))

            existing = None


        if not raw:
            if isinstance(existing,ObjectifyObject):
                if isinstance(val,ObjectifyObject):
                    val = val.to_collection()
                    
                existing.from_collection(val)
                val = existing

        super(ObjectifyDict, self).__setattr__(name,val)

    def __getattribute__(self,name,raw=False):
        if name[-2:] == "__" and name[:2] == "__":
            return super(ObjectifyDict, self).__getattribute__(name)

        try:
            existing = super(ObjectifyDict, self).__getattribute__(name)
        except Exception as e:
            existing = None
        
        if not raw:
            if isinstance(existing,ObjectifyObject) and not isinstance(existing,ObjectifyModel):
                if raw:
                    return existing
                return existing.to_collection()
        
        return super(ObjectifyDict, self).__getattribute__(name)

    def __setitem__(self,key,value):
        self.__setattr__(key,value)

    def __getitem__(self,key):
        return self.__getattribute__(key)

    def __setattr_dynamic__(self,name,val):

        if name in self.__obj_attrs__:
            raise RuntimeError("Attempted introduction of dynamic attribute clashes with existing attributes")

        if (self.__dynamic_class__ is not None and
                self.__dynamic_class__ is not False and 
                not isinstance(self.__dynamic_class__,ObjectifyObject)):
            raise RuntimeError("__dynamic_class__ MUST be an instance of ObjectifyObject if it is set")

        if not self.__dynamic_class__ and not self.__allow_classed_dynamics__:
            raise RuntimeError("To introduce dynamic attributes, please use __dynamic_class__ and/or __allow_classed_dynamics__")

        #We have a dynamic class
        #We dont allow classed dynamics
        #The introduced object is an instance of ObjectifyObject
        #BUT it isnt not an instance of our dynamic class
        if (self.__dynamic_class__ and 
                not self.__allow_classed_dynamics__ and 
                isinstance(val,ObjectifyObject) and
                not isinstance(val,self.__dynamic_class__.__class__)):

            raise RuntimeError("Introduction of dynamic attributes which are not ObjectifyObjects MUST be instances of __dynamic_class__")


        self.__obj_attrs__[name] = name
        if not isinstance(val,ObjectifyObject):
            
            obj = self.__dynamic_class__.duplicate_inited()
            obj.name = name
            obj.from_collection(val)
            super(ObjectifyDict, self).__setattr__(name,obj)
        else:
            val.name = name
            super(ObjectifyDict, self).__setattr__(name,val)

    def set_raw_attribute(self,name,val):
        return self.__setattr__(name,val,raw=True)

    def get_raw_attribute(self,name):
        return self.__getattribute__(name,raw=True)

    def to_collection(self):
        to_return = {}

        for attr,obj in self.__dict__.iteritems():
            if isinstance(obj,ObjectifyProperty):
                if not obj._auto_fetch_set:
                    #Auto fetch not specifically set
                    if not obj.auto_fetch and attr in self.fetch_attrs:
                        obj.auto_fetch = True
                        to_return[obj.name] = obj.value
                        obj.auto_fetch = False
                    else:
                        to_return[obj.name] = obj.value

                else:
                    to_return[obj.name] = obj.value
            elif isinstance(obj,ObjectifyObject):
                to_return[obj.name] = obj.to_collection()


        return to_return

    def from_collection(self,dict,clear=True):
        #Clear out existing attributes
        if clear:
            for _,attr in self.__obj_attrs__.iteritems():
                if _ in dict:
                    continue

                obj = self.__getattribute__(attr,raw=True)
                obj = obj.duplicate_inited()
                self.__setattr__(attr,obj,raw=True)
                
        for attr,obj in dict.iteritems():
            if attr not in self.__obj_attrs__:
                continue

            name = self.__obj_attrs__[attr]

            self.__setattr__(name,obj)
    
    def fetch(self):
        _id = getattr(self,self.__fetch_attr__)
        return self.fetch_from(_id)

    def duplicate_inited(self,keep_name=True):
        if keep_name:
            self.__init_kwargs__['name'] = self.name

        cl = self.__class__(
            *self.__init_args__,
            **self.__init_kwargs__
        )

        for _,attr in cl.__obj_attrs__.iteritems():
            cl.set_raw_attribute(
                attr,
                cl.get_raw_attribute(attr).duplicate_inited()
            )
        
        return cl