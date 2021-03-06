import webapp2
import jinja2
import os
import datetime
import json
import time

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from task import Task
from board import Board

class TaskUpdateRequestProcess( webapp2.RequestHandler ):
    def post( self, board_key ):
        self.response.headers[ 'Content-Type' ] = 'application/json'
        user = users.get_current_user()
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()

        request_data = self.request.body
        data_list = request_data.split('&')
        cta_action = data_list[len(data_list)-1].split('=')[1]

        if cta_action == "update-task-assignment":
            member_key = data_list[0].split('=')[1]
            task_index = int(data_list[2].split('=')[1])
            board_index = data_list[3].split('=')[1]
            board = ndb.Key('Board', int(board_key)).get()

            if not str(logged_user.key.id()) in board.members:
                message = 'Access Denied. Your membership has been revoked.'
                query_string = '?failed=' + message
                url = '/boards' + query_string
                self.response.write( json.dumps( {"url": url } ) )
                return

            board.tasks[task_index].assigned_to = member_key
            board.tasks[task_index].high_lighted = False
            board.put()
            self.response.write( json.dumps( {"url": '/boards/' + board_key + '/' + board_index } ) )
            return
        elif cta_action == "update-task-completed":
            completed = True if data_list[0].split('=')[1].capitalize() == "True" else False
            task_index = int(data_list[2].split('=')[1])
            board_index = data_list[3].split('=')[1]
            board = ndb.Key('Board', int(board_key)).get()

            if not str(logged_user.key.id()) in board.members:
                message = 'Access Denied. Your membership has been revoked.'
                query_string = '?failed=' + message
                url = '/boards' + query_string
                self.response.write( json.dumps( {"url": url } ) )
                return

            board.tasks[task_index].completed = completed
            response_dict = {}
            if completed:
                board.tasks[task_index].completed_on = datetime.datetime.now()
            else:
                board.tasks[task_index].completed_on = None
            board.put()
            response_dict['completed'] = completed
            response_dict['completed_on'] = time.mktime(board.tasks[task_index].completed_on.timetuple()) if completed else None
            response_dict['task_title'] = board.tasks[task_index].title
            response_dict['task_index'] = task_index
            response_dict['url'] = '/boards/' + board_key + '/' + board_index
            self.response.write( json.dumps( response_dict ) )
            return
