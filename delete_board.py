import webapp2
import jinja2
import os
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from board import Board

class DeleteBoardPage( webapp2.RequestHandler ):
    def get( self, board_key, board_index ):
        user = users.get_current_user()
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()
        board = ndb.Key('Board', int(board_key))
        board_members = board.get().members

        if not str(logged_user.key.id()) in board_members:
            message = 'Access Denied. Your membership has been revoked.'
            query_string = '?failed=' + message
            url = '/boards' + query_string
            self.redirect( url )

        board_title = board.get().title
        logged_user.boards.remove(str(board.get().key.id()))
        logged_user.put()
        board.delete()
        message = board_title.capitalize() + ' Board deleted successfully'
        query_string = '?success=' + message
        url = '/boards' + query_string
        self.redirect(url)
        pass
