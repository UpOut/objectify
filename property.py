# coding: utf-8

from .base import ObjectifyObject

class ObjectifyProperty(ObjectifyObject):

    to_type = None
    #Should be an APIObject
    fetch_object = None

    name = None

    #Value passed to property
    __value__ = None
    #Whether or not the value was specifically set (is it default?)
    __value_set__ = False
    #If we've fetched the value
    __value_fetched__ = False
    #The value we retrieved on fetch
    __value_retrieved__ = None
    #The value used to fetch
    __value_fetched_value__ = None

    def __init__(self,name=None,fetch_key=False,default=None,
            auto_fetch_default=False,auto_fetch=None):
        super(ObjectifyProperty, self).__init__(
            name=name, 
            fetch_key=fetch_key,
            default=default,
            auto_fetch_default=auto_fetch_default,
            auto_fetch=auto_fetch
        )

        self.name = name
        self.fetch_key = fetch_key
        self.default = default
        self.__value__ = default
        self.__value_set__ = False

        if auto_fetch is not None:
            self._auto_fetch_set = True
            self.auto_fetch = auto_fetch
        else:
            self._auto_fetch_set = False
            if not self.fetch_object:
                self.auto_fetch = False
            else:
                self.auto_fetch = True

        if self.auto_fetch and not self.fetch_object:
            raise RuntimeError("Cannot auto_fetch property without fetch_object")

        self.auto_fetch_default = auto_fetch_default
        self.__value_fetched__ = False
        self.__value_retrieved__ = None
        self.__value_fetched_value__ = None

    def _to_type(self,value):
        return self.to_type(value)

    def fetch(self):
        if not self.fetch_object:
            raise RuntimeError("Cannot fetch value without fetch_object")

        _do_fetch = True
        if self.__value_fetched__:
            if self.__value_fetched_value__ == self.__value__:
                _do_fetch = False


        if _do_fetch:
            self.__value_fetched_value__ = self.__value__
            self.__value_fetched__ = True
            self.__value_retrieved__ = self.fetch_object.duplicate_inited()
            self.__value_retrieved__.fetch_from(self.__value__)
            self.__value_retrieved__ = self.__value_retrieved__.to_collection()

        return self.__value_retrieved__

    def from_collection(self,frm):
        self.__value__ = self._to_type(frm)

        self.__value_fetched__ = False
        self.__value_set__ = True

    def to_collection(self):
        if self.__value_set__:
            if self.auto_fetch:
                return self.fetch()
            else:
                if self.__value_fetched__:
                    #Enable calling of .fetch() manually
                    return self.__value_retrieved__
                else:
                    return self.__value__
        else:
            if self.auto_fetch_default:
                return self.fetch()
            else:
                if self.__value_fetched__:
                    #Enable calling of .fetch() manually
                    return self.__value_retrieved__
                else:
                    return self.__value__

    @property
    def value(self):
        return self.to_collection()        

    @value.setter
    def value(self,value):
        self.from_collection(value)

    def duplicate_inited(self,keep_name=True):
        if keep_name:
            self.__init_kwargs__['name'] = self.name

        return self.__class__(
            *self.__init_args__,
            **self.__init_kwargs__
        )
