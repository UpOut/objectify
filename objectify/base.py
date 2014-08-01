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

    def fetch_from(self,frm):
        raise NotImplementedError()


    def saveable_collection(self):
        return self.to_collection()
        
        
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
"""



    TOP LEVEL LOADERS:
        WHY NECESSARY:
            In certain cases we need to load lower level objects by a top level attribute
        ALTERNATIVE:
            Passing attributes down to lower level objects before loading them. 
            THIS CANNOT JUST BE DONE ON TOP LEVEL LOAD! Reason is we may want to call the lower level load without loading the top level

            This should be done when an attribute is 

"""