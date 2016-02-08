# coding: utf-8

from ..base import ObjectifyObject

class ObjectifyProperty(ObjectifyObject):

    to_type = None
    #Should be an ObjectifyObject
    #Object to use to fetch
    __fetch_object__ = None
    #Execute this function with the value of this property
    #Use what it returns to fetch
    __fetch_wrapper_func__ = None

    __passdown_to_fetch_object__ = None

    name = None

    #Value passed to property
    __value__ = None
    #Whether or not the value was specifically set externally, default or not
    __value_touched__ = False
    #If we've fetched the value
    __value_fetched__ = False
    #The value we retrieved on fetch
    __value_retrieved__ = None
    #The value used to fetch
    __value_fetched_value__ = None

    def __init__(self,name=None,fetch_key=False,
            default=None,can_fetch_default=True,
            auto_fetch_default=False,auto_fetch=None,*args,**kwargs):

        super(ObjectifyProperty, self).__init__(
            *args,
            name=name, 
            fetch_key=fetch_key,
            default=default,
            can_fetch_default=can_fetch_default,
            auto_fetch_default=auto_fetch_default,
            auto_fetch=auto_fetch,
            **kwargs
        )

        self.__key_name__ = name
        self.__fetch_key__ = fetch_key
        
        self.incoming_default = default

        if 'incoming_default' in kwargs:
            self.incoming_default = kwargs['incoming_default']

        self.outgoing_default = default
        if 'outgoing_default' in kwargs:
            self.outgoing_default = kwargs['outgoing_default']

        self.__value__ = self.outgoing_default
        self.__value_touched__ = False

        if auto_fetch is not None:
            self._auto_fetch_set = True
            self.auto_fetch = auto_fetch
        else:
            self._auto_fetch_set = False
            if not self.__fetch_object__:
                self.auto_fetch = False
            else:
                self.auto_fetch = True

        if self.auto_fetch and not isinstance(self.__fetch_object__,ObjectifyObject):
            raise RuntimeError("Cannot auto_fetch property without fetch_object that is an ObjectifyObject")

        if isinstance(__fetch_object__,ObjectifyObject):
            self.__fetch_object__ = __fetch_object__.copy_inited()

        self.auto_fetch_default = auto_fetch_default
        if self.auto_fetch_default:
            #If we are auto fetching default we have to be able to!
            can_fetch_default = True

        self.can_fetch_default = can_fetch_default
        self.__value_fetched__ = False
        self.__value_retrieved__ = None
        self.__value_fetched_value__ = None
        self.__passdown_to_fetch_object__ = None
        self.__passdown_from__ = kwargs.get("passdown_from",None)


    def _add_passdown_value(self,to_attr,data):
        if not self.__passdown_to_fetch_object__:
            self.__passdown_to_fetch_object__ = {}

        if not isinstance(self.__fetch_object__,ObjectifyObject):
            raise RuntimeError("Must have a fetch object to handle passdowns!")

        self.__passdown_to_fetch_object__[to_attr] = data

        raw_child = self.__fetch_object__.get_raw_attribute(to_attr)

        raw_child.from_collection(
            data
        )

    def _setup_passdown(self,to_object):

        if (self.__passdown_to_fetch_object__ and
                isinstance(to_object,ObjectifyObject)):

            for to_attr, data in self.__passdown_to_fetch_object__.iteritems():

                raw_child = to_object.get_raw_attribute(to_attr)
                
                raw_child.from_collection(
                    data
                )
    

    def _access_fetch_object(self):
        return self.__fetch_object__

    def _to_type(self,value):
        return self.to_type(value)

    def _outgoing_convert(self,value):
        return value

    def empty(self):
        if not self.__value_touched__:
            return True

        return self.is_default()

    def is_default(self):
        if self.__value__ == self.outgoing_default:
            return True
        return False

    def fetch(self,fetch_from_kwargs={}):
        if self.is_default() and not self.can_fetch_default:
            return self.__value_retrieved__

        if not isinstance(self.__fetch_object__,ObjectifyObject):
            raise RuntimeError("Cannot fetch value without fetch_object")

        _fetch_value = self.__value__
        if isinstance(_fetch_value,ObjectifyObject):
            _fetch_value = _fetch_value.to_collection()
        

        _do_fetch = True
        if self.__value_fetched__:
            if self.__value_fetched_value__ == _fetch_value:
                _do_fetch = False

        if _do_fetch:
            self.__value_fetched_value__ = _fetch_value
            self.__value_fetched__ = True
            self.__value_retrieved__ = self.__fetch_object__.copy_inited()
                
            self._setup_passdown(self.__value_retrieved__)

            fetch_from = _fetch_value
            if self.__fetch_wrapper_func__ is not None:
                fetch_from = self.__fetch_wrapper_func__(fetch_from)

            self.__value_retrieved__.fetch_from(fetch_from,**fetch_from_kwargs)

        return self.__value_retrieved__

    def from_collection(self,frm):

        if (frm == self.incoming_default or
                frm == self.outgoing_default):
            self.__value__ = self.outgoing_default
        else:    
            self.__value__ = self._to_type(frm)

        self.__value_touched__ = True
        self.__value_fetched__ = False

    def to_collection(self):
        if self.is_default() and self.auto_fetch_default:
            self.fetch()
        elif not self.is_default() and self.auto_fetch:
            self.fetch()
        
        if self.__value_fetched__:
            #Enable calling of .fetch() manually
            return self.__value_retrieved__.to_collection()
        else:
            return self._outgoing_convert(self.__value__)

    @property
    def value(self):
        return self.to_collection()        

    @value.setter
    def value(self,value):
        self.from_collection(value)

    def copy_inited(self,keep_name=True):
        if keep_name:
            self.__init_kwargs__['name'] = self.__key_name__

        return self.__class__(
            *self.__init_args__,
            **self.__init_kwargs__
        )
