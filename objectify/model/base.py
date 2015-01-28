# coding: utf-8

import json

from ..base import ObjectifyObject

class ObjectifyModel(ObjectifyObject):
    __fetch_attr__ = None
    
    __serializer__ = json.dumps
    __deserializer__ = json.loads
    
    __key_name__ = None
    __fetch_attrs__ = None
    __fetch_key__ = None

    def __init__(self,name=None,fetch_key=False,fetch_attrs=[],
            serializer=None,deserializer=None,**kwargs):
        super(ObjectifyModel, self).__init__(
            name=name,
            fetch_key=fetch_key,
            fetch_attrs=fetch_attrs,
            serializer=serializer,
            deserializer=deserializer,**kwargs
        )

        self.__key_name__ = name
        self.__fetch_attrs__ = set(fetch_attrs)
        self.__fetch_key__ = fetch_key

        if serializer is not None:
            self.__serializer__ = serializer
        
        if deserializer is not None:
            self.__deserializer__ = deserializer

        default = kwargs.get("default",None)
        if default:
            self.from_collection(default)


    def fetch_key_value(self):
        return getattr(self,self.__fetch_attr__)

    def serialize(self):
        return self.__serializer__(self.to_collection())

    def deserialize(self,val):
        return self.from_collection(
            self.__deserializer__(val)
        )

    def copy_inited(self,keep_name=True):
        if keep_name:
            self.__init_kwargs__['name'] = self.__key_name__

        return self.__class__(
            *self.__init_args__,
            **self.__init_kwargs__
        )