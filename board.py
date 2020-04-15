from google.appengine.ext import ndb

from task import Task

class Board( ndb.Model ):
    title = ndb.StringProperty()
    created_by = ndb.StringProperty()
    created_at = ndb.StringProperty()
    members = ndb.StringProperty( repeated = True )
    tasks = ndb.StructuredProperty( Task, repeated = True )
