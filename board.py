from google.appengine.ext import ndb

from task import Task

class Board( ndb.Model ):
    title = ndb.StringProperty()
    created_by = ndb.StringProperty()
    created_at = ndb.DateProperty()
    updated_at = ndb.DateProperty()
    members = ndb.StringProperty( repeated = True )
    tasks = ndb.StructuredProperty( Task, repeated = True )
