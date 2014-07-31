# coding: utf-8

import json

from ..base import ObjectifyObject

class ObjectifyModel(ObjectifyObject):
    __fetch_attr__ = None
    
    __serializer__ = json.dumps
    __deserializer__ = json.loads
    
    name = None
    fetch_attrs = None
    fetch_key = None

    def __init__(self,name=None,fetch_key=False,fetch_attrs=[],
            serializer=None,deserializer=None,**kwargs):
        super(ObjectifyModel, self).__init__(
            name=name,
            fetch_key=fetch_key,
            fetch_attrs=fetch_attrs,
            serializer=serializer,
            deserializer=deserializer,**kwargs
        )

        self.name = name
        self.fetch_attrs = set(fetch_attrs)
        self.fetch_key = fetch_key

        self.__fetch_attr__ = None
        if serializer is not None:
            self.__serializer__ = serializer
        
        if deserializer is not None:
            self.__deserializer__ = deserializer


    def serialize(self):
        return self.__serializer__(self.to_collection())

    def deserialize(self,val):
        return self.from_collection(
            self.__deserializer__(val)
        )

    def copy_inited(self,keep_name=True):
        if keep_name:
            self.__init_kwargs__['name'] = self.name

        return self.__class__(
            *self.__init_args__,
            **self.__init_kwargs__
        )