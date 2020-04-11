from google.appengine.ext import ndb

class Task( ndb.Model ):
    title = ndb.StringProperty()
    due_date = ndb.DateProperty()
    completed = ndb.BooleanProperty()
    created_by = ndb.StringProperty()
    assigned_to = ndb.StringProperty()
    created_at = ndb.DateProperty()
