# coding: utf-8

class ObjectifyObject(object):

    __init_args__ = []
    __init_kwargs__ = {}

    def __init__(self,*args,**kwargs):
        self.__init_args__ = args
        self.__init_kwargs__ = kwargs

    def __repr__(self):
        return '<%s.%s object at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
        )
    
    def fetch(self):
        raise NotImplementedError()

    def fetch_from(self,frm,**kwargs):
        raise NotImplementedError()

    def transform_fetch(self,fetched):
        raise NotImplementedError()
        
    def to_collection(self):
        raise NotImplementedError()

    def from_collection(self,frm):
        raise NotImplementedError()


    #Return a duplicate object with the init args/kwargs used
    def copy_inited(self):
        return self.__class__(
            *self.__init_args__,
            **self.__init_kwargs__
        )

    #Lets us specify an example for this object
    #Designed for docs
    def example_value(self):
        raise NotImplementedError()