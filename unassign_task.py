import webapp2
import jinja2
import os
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from board import Board

class UnassignTaskInTaskBoard( webapp2.RequestHandler ):
    def get( self, board_key, board_index, task_index ):
        board = ndb.Key('Board', int(board_key)).get()
        board.tasks[int(task_index)-1].assigned_to = ''
        board.put()
        url = '/boards/' + board_key + '/' + board_index
        self.redirect(url)
        pass
