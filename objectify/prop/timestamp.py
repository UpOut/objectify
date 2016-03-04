# coding: utf-8

import pytz
from dateutil.parser import parse as dateutil_parse

from datetime import datetime, date
from .base import ObjectifyProperty

class SmartTimestamp(ObjectifyProperty):
    """ A timestamp

        Attempts to normalize any valid incoming
        timestamp into one format, and may convert timezone

        Uses python dateutil for incoming validation
    """

    __to_timezone__ = None
    #If true, will convert to the to_timezone
    __timezone_convert__ = False
    #Used in timezone conversion if datetime does not have one
    __from_timezone__ = None

    #Collection format
    __outgoing_format__ = '%Y-%m-%d %H:%M:%S'

    to_type=datetime

    def __init__(self,*args,**kwargs):
        super(SmartTimestamp, self).__init__(
            *args,
            **kwargs
        )

        self.__to_timezone__ = kwargs.get("to_timezone",None)
        self.__timezone_convert__ = kwargs.get("timezone_convert",False)
        self.__from_timezone__ = kwargs.get("from_timezone",None)

        _outgoing_format = kwargs.get("outgoing_format",None)
        if _outgoing_format:
            self.__outgoing_format__ = _outgoing_format

    def _to_type(self,value):
        if isinstance(value,date) and not isinstance(value,datetime):
            value = datetime.combine(value, datetime.min.time())
            
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

    def _outgoing_convert(self,value):
        if value and isinstance(value, datetime):
            return value.strftime(self.__outgoing_format__)

        return value

    
    def example_value(self):
        return "2016-03-02T18:36:14+00:00"