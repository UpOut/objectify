# coding: utf-8

import copy

from .base import ObjectifyModel
from ..base import ObjectifyObject
from ..meta import ObjectifyDictType
from ..prop.base import ObjectifyProperty

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



    """
        The attribute used to fetch data about this object
    """
    __fetch_attr__ = None


    """
        Set of attributes to exclude from the collection this object generates
        NOT from the "from_collection" attribute
    """
    __exclude_from_collection__ = []

    """
        Exclude empty values from generated collection
        Can be "True" or "False" or a last of attribute names to exclude e.g.
        ["name","date"]
    """
    __exclude_empty__ = False

    """
        This set of attributes is a map of attributes that this object should 
        pass down to other attributes, and which attributes they should be passed to

        Format:
        {
            "from_attr" : [
                ("to_attr.__key_name__","child_attr")
            ]
        }

        When "self_attr" is set, the attribute "self_attr_2_attr" will also be set.
        "self_attr_2_attr" is a child attribute of "self_attr_2", which is also an attribute of self
    """
    __passdown_attributes__ = {}

    """
        Attributes from which to passdown and the attributes which they will be passed to
        Format:
        {
            "parent_attr" : "self_attr"
        }
    """
    __passdown_from__ = None

    def __init__(self,*args,**kwargs):
        self.__fetch_attr__ = None
        self.__obj_attrs__ = self.__obj_attrs__.copy()

        self.__passdown_attributes__ = self.__passdown_attributes__.copy()

        _exclude_from_collection = kwargs.get("exclude_from_collection",None)
        if _exclude_from_collection is not None:
            self.__exclude_from_collection__ = set(_exclude_from_collection)
        else:
            self.__exclude_from_collection__ = set(self.__exclude_from_collection__)

        _exclude_empty = kwargs.get("exclude_empty",None)
        if _exclude_empty is not None:
            self.__exclude_empty__ = _exclude_empty

        if isinstance(self.__exclude_empty__,list):
            self.__exclude_empty__ = set(self.__exclude_empty__)

        self.__passdown_from__ = kwargs.get("passdown_from",None)

        if self.__passdown_from__ is not None:
            if not isinstance(self.__passdown_from__,dict):
                raise RuntimeError("passdown_from MUST be a dictionary")


        if (self.__dynamic_class__ is not None and 
                not isinstance(self.__dynamic_class__,ObjectifyObject)):
            raise RuntimeError("__dynamic_class__ MUST be an instance of ObjectifyObject if it is set")

        self._isolate_attributes()

        super(ObjectifyDict, self).__init__(*args,**kwargs)

    def __setattr__(self,name,val,raw=False):


        if name[-2:] == "__" and name[:2] == "__":
            return super(ObjectifyDict, self).__setattr__(name,val)
        
        existing = None
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
            from ..dynamic import Dynamic
            if isinstance(existing,Dynamic):
                return self.__set_dynamic_attr__(name,val)

            if isinstance(existing,ObjectifyObject):
                if isinstance(val,ObjectifyObject):
                    val = val.to_collection()
                
                _val = existing#.copy_inited()
                _val.from_collection(val)

                val = _val

        super(ObjectifyDict, self).__setattr__(name,val)

        if not raw:
            self.__handle_passdown__(name)

    def __getattribute__(self,name,raw=False):
        if name[-2:] == "__" and name[:2] == "__":
            return super(ObjectifyDict, self).__getattribute__(name)

        try:
            existing = super(ObjectifyDict, self).__getattribute__(name)
            if raw:
                return existing

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
            This function handles setting attributes which are instances of objectify.dynamic.Dynamic
        """

        try:
            existing = super(ObjectifyDict, self).__getattribute__(name)
        except Exception as e:
            raise RuntimeError("Cannot use __set_dynamic_attr__ on a attribute which is not an instance of Dynamic")

        from ..dynamic import Dynamic
        if not isinstance(existing,Dynamic):
            raise RuntimeError("Cannot use __set_dynamic_attr__ on a attribute which is not an instance of Dynamic")


        if isinstance(val,ObjectifyModel):
            """
                A dynamic attribute simply wants to adapt any value to the closest ObjectifyObject representation
                In this case we already have a best fit, which is the raw value
            """
            super(ObjectifyDict, self).__setattr__(name,val)
            self.__handle_passdown__(name)
            return

        """
            This function handles setting attributes which are or subclass
            our Dynamic property
        """

        if isinstance(val,dict):
            """
                In this case we need to create a DynamicDict object to properly fit our data
            """

            from ..dynamic import DynamicDict
            _val = DynamicDict(name=name)
            _val.from_collection(val)

            super(ObjectifyDict, self).__setattr__(name,_val)
            self.__handle_passdown__(name)
            return

        if isinstance(val,list):
            """
                In this case we need to create a DynamicList object to properly fit our data
            """
            from ..dynamic import DynamicList
            _val = DynamicList(name=name)
            _val.from_collection(val)

            super(ObjectifyDict, self).__setattr__(name,_val)
            self.__handle_passdown__(name)
            return
        

        _val = existing#.copy_inited()
        _val.from_collection(val)
        

        super(ObjectifyDict, self).__setattr__(name,_val)
        self.__handle_passdown__(name)


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

        if self.__dynamic_class__ is None and not self.__allow_classed_dynamics__:
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
            
            obj = self.__dynamic_class__.copy_inited()
            obj.__key_name__ = name
            obj.from_collection(val)

            super(ObjectifyDict, self).__setattr__(name,obj)
        else:
            val.__key_name__ = name
            super(ObjectifyDict, self).__setattr__(name,val)

        self.__handle_passdown__(name)


    def __handle_passdown__(self,data_from):
        if self.__passdown_attributes__ is not None:
            if data_from in self.__passdown_attributes__:
                
                data_to_pass = self.get_raw_attribute(data_from).to_collection()

                for to,to_child in self.__passdown_attributes__[data_from]:
                    raw_to = self.get_raw_attribute(to)

                    if isinstance(raw_to, ObjectifyModel):
                        raw_child = raw_to.get_raw_attribute(to_child)

                        raw_child.from_collection(
                            data_to_pass
                        )
                    elif isinstance(raw_to, ObjectifyProperty):
                            raw_to._add_passdown_value(
                                to_child,
                                data_to_pass
                            )


    def _isolate_attributes(self):
        if self.__dynamic_class__ is not None:
            self.__dynamic_class__ = self.__dynamic_class__.copy_inited()
        
        self.__fetch_attr__ = None
        for _,attr in self.__obj_attrs__.iteritems():
            _obj = self.get_raw_attribute(attr)
            if _obj.__fetch_key__:
                if self.__fetch_attr__ is not None:
                    raise RuntimeError("Object's can only have a single fetch key")
                self.__fetch_attr__ = attr

            self.set_raw_attribute(
                attr,
                _obj.copy_inited()
            )

    def set_raw_attribute(self,name,val):
        return self.__setattr__(name,val,raw=True)

    def get_raw_attribute(self,name):
        return self.__getattribute__(name,raw=True)


    def empty(self,exclude_fetch_key=False):
        exclude = None
        if exclude_fetch_key:
            if self.__fetch_attr__ is not None:
                exclude = set([self.__fetch_attr__])

        return self._empty(exclude=exclude)

    def _empty(self,exclude=None):
        if exclude:
            exclude = set(exclude)

        for _,attr in self.__obj_attrs__.iteritems():
            if exclude is not None and attr in exclude:
                continue

            obj = self.__getattribute__(attr,raw=True)
            if isinstance(obj,ObjectifyObject):
                if not obj.empty():
                    return False

        return True

    def verify_exclude(self,exclude):
        #Raise an exception if we get an empty value

        for ex in exclude:
            if not ex:
                raise RuntimeError("Empty area in exclude path %s in %s" % (exclude,self.__repr__()))


    def split_exclude(self,exclude):
        """
            Returns tuple
            (this level exclude, passdown exclude)
        """
        this_level = set()
        passdown = {}
        for ex in exclude:
            ex_l = ex.split(".")
            self.verify_exclude(ex_l)

            _len = len(ex_l)

            if _len == 0:
                raise RuntimeError("Broken exclude path in %s" % self.__repr__())
            elif _len == 1:
                this_level.add(ex_l[0])
            else:
                if ex_l[0] not in passdown:
                    passdown[ex_l[0]] = set()

                passdown[ex_l[0]].add(".".join(ex_l[1:]))

        return this_level, passdown


    def to_collection(self,exclude=None):
        to_return = {}

        #For notes on the exclude path, see EXCLUDE.rst


        if not exclude:
            exclude = self.__exclude_from_collection__
        else:
            exclude = set(exclude)

        this_level_exclude = None
        passdown_exclude = {}

        if exclude:
            this_level_exclude,passdown_exclude = self.split_exclude(exclude)

        for _,attr in self.__obj_attrs__.iteritems():
            if this_level_exclude is not None and attr in this_level_exclude:
                continue

            obj = self.__getattribute__(attr,raw=True)

            if isinstance(obj,ObjectifyObject):
                if self.__exclude_empty__ == True and obj.empty():
                    continue
                if (isinstance(self.__exclude_empty__, set) and 
                        attr in self.__exclude_empty__ and
                        obj.empty()):
                    continue

                if isinstance(obj,ObjectifyProperty):
                    if not obj._auto_fetch_set:
                        #Auto fetch not specifically set
                        if not obj.auto_fetch and attr in self.__fetch_attrs__:
                            obj.auto_fetch = True
                            try:
                                to_return[obj.__key_name__] = obj.value
                            finally:
                                obj.auto_fetch = False
                        else:
                            to_return[obj.__key_name__] = obj.value

                    else:
                        to_return[obj.__key_name__] = obj.value
                else:
                    if attr in passdown_exclude:
                        to_return[obj.__key_name__] = obj.to_collection(
                            exclude=passdown_exclude[attr]
                        )
                    else:
                        to_return[obj.__key_name__] = obj.to_collection()


        return to_return

    def from_collection_handle_passdown(self,frm,dict,completed=None):
        if completed is None:
            completed = set()


        if frm in completed:
            return completed

        for to,to_child in self.__passdown_attributes__[frm]:
            if to in self.__passdown_attributes__:
                completed = self.from_collection_handle_passdown(to,dict,completed)
            
        if frm in dict:
            if (self.__dynamic_class__ is not None or 
                    self.__allow_classed_dynamics__):
                self.__setattr__(frm,dict[frm])
            else:
                name = self.__obj_attrs__[frm]
                self.__setattr__(name,dict[frm])

        completed.add(frm)    

        return completed


    def from_collection(self,dict,clear=True):
        #Clear out existing attributes

        if clear:
            for _,attr in self.__obj_attrs__.iteritems():
                if _ in dict:
                    continue

                obj = self.__getattribute__(attr,raw=True)
                obj = obj#.copy_inited()
                self.__setattr__(attr,obj,raw=True)
        
        completed = set()
        
        #If we have passdown attributes, we'll want to set those up first
        if self.__passdown_attributes__ is not None:
            for frm in self.__passdown_attributes__.keys():
                completed = self.from_collection_handle_passdown(
                    frm,
                    dict
                )

        for attr,obj in dict.iteritems():
            if attr in completed:
                continue

            if (self.__dynamic_class__ is not None or 
                    self.__allow_classed_dynamics__):
                self.__setattr__(attr,obj)
                continue

            if attr not in self.__obj_attrs__:
                continue

            name = self.__obj_attrs__[attr]

            self.__setattr__(name,obj)

             
    def fetch(self):
        _id = self.fetch_key_value()
        return self.fetch_from(_id)

    def copy_inited(self,keep_name=True):
        if keep_name:
            self.__init_kwargs__['name'] = self.__key_name__

        cl = self.__class__(
            *self.__init_args__,
            **self.__init_kwargs__
        )
        
        return cl
