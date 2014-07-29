==========
Objectify
==========

About
==========

Base object models for API objects.

Allows you to have objects which expand themselves e.g.

{
    "name" : "Will",
    "object" : "12345"
}

In this case we want to be able to expand "object" into the the actual object related to the value 12345, e.g.

{
    "name" : "Will",
    "object" : {
        "id" : "12345",
        "key" : "value",
        ...
    }
}


TODO
==========
Docs

Unit tests

Cleanup classes