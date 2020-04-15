import webapp2
import jinja2
import os
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from task import Task
from board import Board

class TaskUpdateRequestProcess( webapp2.RequestHandler ):
    def post( self, board_key ):
        self.response.headers[ 'Content-Type' ] = 'application/json'
        request_data = self.request.body
        data_list = request_data.split('&')
        cta_action = data_list[len(data_list)-1].split('=')[1]

        if cta_action == "update-task-assignment":
            member_key = data_list[0].split('=')[1]
            task_index = int(data_list[2].split('=')[1])-1
            board = ndb.Key('Board', int(board_key)).get()

            board.tasks[task_index].assigned_to = member_key
            board.put()
            self.response.write( json.dumps( {"response": member_key } ) )
            return
