# coding: utf-8

import pytz
from dateutil.parser import parse as dateutil_parse

from datetime import datetime
from .base import ObjectifyProperty

class SmartDateTime(ObjectifyProperty):
    __to_timezone__ = None
    #If true, will convert to the to_timezone
    __timezone_convert__ = False
    #Used in timezone conversion if datetime does not have one
    __from_timezone__ = None

    to_type=datetime

    def __init__(self,*args,**kwargs):
        super(SmartDateTime, self).__init__(
            *args,
            **kwargs
        )

        self.__to_timezone__ = kwargs.get("to_timezone",None)
        self.__timezone_convert__ = kwargs.get("timezone_convert",None)
        self.__from_timezone__ = kwargs.get("from_timezone",None)

    def _to_type(self,value):
        if not isinstance(value,datetime):
            value = dateutil_parse(value)

        if self.__to_timezone__:
            zone = pytz.timezone(self.__to_timezone__)

            if self.__to_timezone__:
                if self.__timezone_convert__:
                    if value.tzinfo is not None:
                        value = zone.normalize(value.astimezone(zone))
                    else:
                        if not self.__from_timezone__:
                            raise RuntimeError("Could not determine a timezone for datetime %s, use __from_timezone__" % (value))

                        from_zone = pytz.timezone(self.__from_timezone__)

                        value = value.replace(tzinfo=from_zone)
                        value = zone.normalize(value.astimezone(zone))
                        
                else:
                    value = value.replace(tzinfo=zone)

        return value
