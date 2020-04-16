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
from datetime import datetime as str_datetime

start = os.path.dirname( __file__ )
rel_path = os.path.join(start, 'templates')
abs_path = os.path.realpath(rel_path)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class EditTaskOnTaskBoard( webapp2.RequestHandler ):
    def get( self, board_key, board_index, task_index ):
        self.response.headers[ 'Content-Type' ] = 'text/html'

        url = ''
        logged_user = None
        user = users.get_current_user()
        has_completed_profile = False
        firstname = ''
        lastname = ''
        initials = ''
        username = ''
        has_params = False
        params_key = ''
        params_value = ''

        try:
            if self.request.params.get('success') != None:
                has_params = True
                params_key = 'success'
                params_value = self.request.params.get('success')
                firstname = '' if self.request.params.get('firstname') == None else self.request.params.get('firstname')
                lastname = '' if self.request.params.get('lastname') == None else self.request.params.get('lastname')
            elif self.request.params.get('failed') != None:
                has_params = True
                params_key = 'failed'
                params_value = self.request.params.get('failed')
                firstname = '' if self.request.params.get('firstname') == None else self.request.params.get('firstname')
                lastname = '' if self.request.params.get('lastname') == None else self.request.params.get('lastname')
        except:
            pass

        if user:
            url = users.create_logout_url( self.request.uri )

            logged_user_key = ndb.Key( 'User', user.user_id() )
            logged_user = logged_user_key.get()

            if logged_user == None:
                logged_user = User( id = user.user_id() )
                logged_user.put()

            else:
                if not logged_user.firstname:
                    has_completed_profile = False
                else:
                    has_completed_profile = True
                    firstname = logged_user.firstname
                    lastname = logged_user.lastname
                    username = firstname + ' ' + lastname
                    initials = self.getLoggedUserInitials( username )

        else:
            url = users.create_login_url( self.request.uri )
            self.redirect( url )
            return

        board = ndb.Key('Board', int(board_key)).get()

        if not str(logged_user.key.id()) in board.members:
            message = 'Access Denied. Your membership has been revoked.'
            query_string = '?failed=' + message
            url = '/boards' + query_string
            self.redirect( url )

        template_values = {
            'url': url,
            'logged_user': logged_user,
            'user': user,
            'completed_profile': has_completed_profile,
            'firstname': firstname,
            'lastname': lastname,
            'initials': initials,
            'username': username,
            'has_params': has_params,
            'params_key': params_key,
            'params_value': params_value,
            'show_main_label': True,
            'main_label': 'Update Task',
            'main_label_icon': "fas fa-tasks fa-2x",
            'board_key': board_key,
            'board_index': int(board_index),
            'task_index': task_index,
            'members_json': json.dumps( [] ),
            'member_ids': json.dumps( [] ),
            'task': board.tasks[int(task_index)]
        }

        template = JINJA_ENVIRONMENT.get_template( 'pages/edit_task.html' )
        self.response.write( template.render( template_values ) )
        return


    def post( self, board_key, board_index, task_index ):
        self.response.headers[ 'Content-Type' ] = 'text/html'
        cta_button = self.request.get( 'button' )
        task_title = str(self.request.get( 'task_title' ))
        due_date = self.request.get( 'due_date' )
        task_desc = self.request.get( 'task_desc' )

        if cta_button == 'Update Task':
            if task_title == '' or due_date == '':
                message = "Task title and Due date fields must be completed to proceed"
                query_string = "?failed=" + message + "&task_title=" + task_title + "&due_date=" + due_date
                url = "/boards/" + board_key + "/" + board_index + "/" + task_index + "/edit-task" + query_string
                self.redirect( url )
                return
            else:
                board = ndb.Key( 'Board', int(board_key) ).get()
                board.tasks[int(task_index)]
                due_date = str_datetime.strptime(str(due_date), '%Y-%m-%d').date()

                board.tasks[int(task_index)].title = task_title
                board.tasks[int(task_index)].due_date = due_date
                board.tasks[int(task_index)].description = task_desc
                board.put()
                url = "/boards/" + board_key + "/" + board_index
                self.redirect( url )
                return

    def getLoggedUserInitials( self, username ):
        name_list = username.split(' ')
        word_count = len(name_list)
        if word_count == 1:
            return (name_list[0][0] + name_list[0][1]).upper()
        elif word_count > 1:
            return (name_list[0][0] + name_list[1][0]).upper()

    def isTaskNameUniqueOnBoard( self, tasks, task_title ):
        is_task_unique = True

        for task in tasks:
            if task.title.lower() == task_title.lower():
                is_task_unique = False

        return is_task_unique
