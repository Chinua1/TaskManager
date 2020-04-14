from google.appengine.ext import ndb

from task import Task

class Board( ndb.Model ):
    title = ndb.StringProperty()
    created_by = ndb.StringProperty()
    created_at = ndb.StringProperty()
    members = ndb.StringProperty( repeated = True )
    tasks = ndb.StructuredProperty( Task, repeated = True )
    is_saved = False

    @classmethod
    def _post_put_hook( self, future):
        if future.state == future.FINISHING:
            self.is_saved = True
        else:
            self.is_saved = False
