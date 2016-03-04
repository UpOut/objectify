# coding: utf-8

import ujson
from objectify import ObjectifyDict, ObjectifyList
from objectify.dynamic import DynamicDict

from objectify.prop import String, Integer, Boolean, Decimal, TrimmedUnicode
from objectify.dynamic import DynamicProperty
from objectify.prop.timestamp import SmartTimestamp

from dateutil.parser import parse as dateutil_parse
print DynamicProperty.__doc__

class DecimalLatitude(Decimal):
    __decimal_context_kwargs__ = {
        "prec" : 7
    }


class Test(ObjectifyDict):
    d = DecimalLatitude()

    x = Boolean()

    y = SmartTimestamp()

    w = DynamicDict()

    t = TrimmedUnicode()

z = Test()
z.from_collection({
    "d" : "99.123456789"
})
print z.d.normalize()
print type(z.d)

print Integer().example_value()

print ujson.encode(Test().example_value())




"""
class _UserActionsDynamic(ObjectifyDict):
    __dynamic_class__ = None
    __allow_classed_dynamics__ = True
    
class UserActionDataContainer(ObjectifyDict):
    generated_map = Dynamic()
    raw_string = String()
    
class UserActionObject(ObjectifyDict):
    id = String("@id")
    category = String("@category")
    category_description = String("@category_description")


    request_date = String("@request_date")
    received_date = String("@received_date")
    queued_date = String("@queued_date")
    recorded_date = String("@recorded_date")


    user_id = String("@upout_user_id")
    subscriber_id = String("@insiders_subscriber_id")

    data = UserActionDataContainer("@data")

class UserActionContainer(ObjectifyDict):
    action_last = UserActionObject()
    action_history = ObjectifyList(UserActionObject())



class UserObject(ObjectifyDict):
    test = String(fetch_key=True)
    testah = String()
    #actions = _UserActionsDynamic()

zzz = UserObject()


_actions = {}

print id(UserActionContainer.action_history)
for z in xrange(1):
    for i in xrange(2):
        if str(i) not in _actions:
            _actions[str(i)] = UserActionContainer()
        data = '{"cool":"story","bro":1.5,"neat":2}'
        obj = UserActionObject()
        
        #_container = UserActionDataContainer()
        #_container.raw_string = data
        #_container.generated_map = ujson.decode(data)
        #print _container.to_collection()
        
        obj.from_collection({
            "@id" : "action.log_id",
            "@category" : "action.category "+str(i),
            "@category_description" : "action.category_description",
            "@request_date" : "action.request_date",
            "@received_date" : "action.received_date",
            "@queued_date" : "action.queued_date",
            "@recorded_date" : "action.recorded_date",
            "@upout_user_id" : "action.upout_user_id",
            "@insiders_subscriber_id" : "action.upout_subscriber_id",
            "@data" : {
                "generated_map" : ujson.decode(data),
                "raw_string" : data
            }
        })
        
        #print obj.to_collection()
        _actions[str(i)]['action_last'] = obj
        _actions[str(i)]['action_history'].append(obj)
        print _actions[str(i)]['action_history'].to_collection()
        print str(i)
        print id(_actions[str(i)]['action_history'])
"""

"""
zzz = UserObject()
zzz.from_collection({
    "test" : "TESTAH",
    "actions" : _actions
})

print "------------------"
print zzz.to_collection()
"""
