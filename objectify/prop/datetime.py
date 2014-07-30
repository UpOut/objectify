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

    def _to_type(self,value):
        date = dateutil_parse(value)

        if self.__to_timezone__:
            zone = pytz.timezone(self.__to_timezone__)

            if self.__to_timezone__:
                if self.__timezone_convert__:
                    if date.tzinfo is not None:
                        date = zone.normalize(date.astimezone(zone))
                    else:
                        if not self.__from_timezone__:
                            raise RuntimeError("Could not determine a timezone for datetime %s, use __from_timezone__" % (value))

                        from_zone = pytz.timezone(self.__from_timezone__)

                        date = date.replace(tzinfo=from_zone)
                        date = zone.normalize(date.astimezone(zone))
                        
                else:
                    date = date.replace(tzinfo=zone)

        return date
