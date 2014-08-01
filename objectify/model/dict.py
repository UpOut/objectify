# coding: utf-8

import copy

from .base import ObjectifyModel
from ..base import ObjectifyObject
from ..prop import ObjectifyProperty, Dynamic
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

    def __init__(self,*args,**kwargs):
        super(ObjectifyDict, self).__init__(*args,**kwargs)
        self.__obj_attrs__ = self.__obj_attrs__.copy()

        if (self.__dynamic_class__ is not None and 
                not isinstance(self.__dynamic_class__,ObjectifyObject)):
            raise RuntimeError("__dynamic_class__ MUST be an instance of ObjectifyObject if it is set")

        self._isolate_attributes()

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
            if isinstance(existing,Dynamic):
                return self.__set_dynamic_attr__(name,val)

            if isinstance(existing,ObjectifyObject):
                if isinstance(val,ObjectifyObject):
                    val = val.to_collection()
                
                _val = existing#.copy_inited()
                _val.from_collection(val)

                val = _val

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
                return existing.to_collection()
        
        return super(ObjectifyDict, self).__getattribute__(name)

    def __setitem__(self,key,value):
        self.__setattr__(key,value)

    def __getitem__(self,key):
        return self.__getattribute__(key)


    def __set_dynamic_attr__(self,name,val):
        """
            This function handles setting attributes which are instances of objectify.prop.Dynamic
        """

        try:
            existing = super(ObjectifyDict, self).__getattribute__(name)
        except Exception as e:
            raise RuntimeError("Cannot use __set_dynamic_attr__ on a attribute which is not an instance of Dynamic")

        if not isinstance(existing,Dynamic):
            raise RuntimeError("Cannot use __set_dynamic_attr__ on a attribute which is not an instance of Dynamic")


        if isinstance(val,ObjectifyModel):
            """
                A dynamic attribute simply wants to adapt any value to the closest ObjectifyObject representation
                In this case we already have a best fit, which is the raw value
            """
            return super(ObjectifyDict, self).__setattr__(name,val)

        """
            This function handles setting attributes which are or subclass
            our Dynamic property
        """

        if isinstance(val,dict):
            """
                In this case we need to create a DynamicDict object to properly fit our data
            """

            from .dynamic import DynamicDict
            _val = DynamicDict()
            _val.from_collection(val)

            return super(ObjectifyDict, self).__setattr__(name,_val)

        if isinstance(val,list):
            """
                In this case we need to create a DynamicList object to properly fit our data
            """
            from .dynamic import DynamicList
            _val = DynamicList()
            _val.from_collection(val)

            return super(ObjectifyDict, self).__setattr__(name,_val)
        

        _val = existing#.copy_inited()
        _val.from_collection(val)
        

        super(ObjectifyDict, self).__setattr__(name,_val)


    def __setattr_dynamic__(self,name,val):
        """
            This function handles setting dynamic attributes with rules defined with
            __dynamic_class__ and __allow_classed_dynamics__
        """
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
            
            obj = self.__dynamic_class__#.copy_inited()
            obj.__key_name__ = name
            obj.from_collection(val)
            super(ObjectifyDict, self).__setattr__(name,obj)
        else:
            val.__key_name__ = name
            super(ObjectifyDict, self).__setattr__(name,val)

    def _isolate_attributes(self):
        if self.__dynamic_class__ is not None:
            self.__dynamic_class__ = self.__dynamic_class__.copy_inited()
            
        for _,attr in self.__obj_attrs__.iteritems():
            self.set_raw_attribute(
                attr,
                self.get_raw_attribute(attr).copy_inited()
            )

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
                    if not obj.auto_fetch and attr in self.__fetch_attrs__:
                        obj.auto_fetch = True
                        to_return[obj.__key_name__] = obj.value
                        obj.auto_fetch = False
                    else:
                        to_return[obj.__key_name__] = obj.value

                else:
                    to_return[obj.__key_name__] = obj.value
            elif isinstance(obj,ObjectifyObject):
                to_return[obj.__key_name__] = obj.to_collection()


        return to_return

    def from_collection(self,dict,clear=True):
        #Clear out existing attributes

        if clear:
            for _,attr in self.__obj_attrs__.iteritems():
                if _ in dict:
                    continue

                obj = self.__getattribute__(attr,raw=True)
                obj = obj#.copy_inited()
                self.__setattr__(attr,obj,raw=True)
        

        for attr,obj in dict.iteritems():
            if self.__dynamic_class__ or self.__allow_classed_dynamics__:
                self.__setattr__(attr,obj)
                continue

            if attr not in self.__obj_attrs__:
                continue

            name = self.__obj_attrs__[attr]

            self.__setattr__(name,obj)

             
    def fetch(self):
        _id = getattr(self,self.__fetch_attr__)
        return self.fetch_from(_id)

    def copy_inited(self,keep_name=True):
        if keep_name:
            self.__init_kwargs__['name'] = self.__key_name__

        cl = self.__class__(
            *self.__init_args__,
            **self.__init_kwargs__
        )
        
        return cl
