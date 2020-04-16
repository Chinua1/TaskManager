import webapp2
import jinja2
import os
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from board import Board

class DeleteTaskFromTaskBoard( webapp2.RequestHandler ):
    def get( self, board_key, board_index, task_index ):
        user = users.get_current_user()
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()
        board = ndb.Key('Board', int(board_key)).get()

        if not str(logged_user.key.id()) in board.members:
            message = 'Access Denied. Your membership has been revoked.'
            query_string = '?failed=' + message
            url = '/boards' + query_string
            self.redirect( url )

        board.tasks.remove(board.tasks[int(task_index)])
        board.put()
        url = '/boards/' + board_key + '/' + board_index
        self.redirect(url)
        pass
