# coding: utf-8

from .base import ObjectifyProperty

TRUE_VALUES = set(['true','1','yes'])
FALSE_VALUES = set(['false','0','no'])

class Boolean(ObjectifyProperty):
    to_type=bool

    def _to_type(self,value):
        if isinstance(value,unicode):
            value = str(value)

        if isinstance(value, basestring):
            _lower = value.lower()
            if _lower in TRUE_VALUES:
                value = True
            elif _lower in FALSE_VALUES:
                value = False
        elif (isinstance(value,int) or 
                isinstance(value,float) or 
                isinstance(value,long)):
            if value == 1:
                value = True
            elif value == 0:
                value = False
        else:
            value = bool(value)

        return value
    
class Bool(Boolean):
    pass