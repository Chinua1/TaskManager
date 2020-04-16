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

from create_board import CreateBoardPage
from board_page import SelectedBoardPage
from home_redirect import RedirectHomeRoute
from invite_member import InviteMemberPage
from add_task import AddTaskPage
from services import TaskUpdateRequestProcess
from delete_task import DeleteTaskFromTaskBoard
from edit_task import EditTaskOnTaskBoard
from unassign_task import UnassignTaskInTaskBoard
from remove_board_member import RemoveMemberFromTaskBoard
from edit_board_name import EditBoardNamePage

start = os.path.dirname( __file__ )
rel_path = os.path.join(start, 'templates')
abs_path = os.path.realpath(rel_path)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class MainPage( webapp2.RequestHandler ):
    def get( self ):
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

        boards = self.getLoggedUserBoards(logged_user.boards)

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
            'main_label': 'Personal Boards',
            'main_label_icon': "far fa-user fa-2x",
            'boards': boards,
            'members_json': json.dumps( [] ),
            'member_ids': json.dumps( [] )
        }

        if user and (not has_completed_profile):
            template = JINJA_ENVIRONMENT.get_template( 'pages/user_info.html' )
            self.response.write( template.render( template_values ) )
            return
        else:
            template = JINJA_ENVIRONMENT.get_template( 'pages/index.html' )
            self.response.write( template.render( template_values ) )
            return


    def post( self ):
        self.response.headers[ 'Content-Type' ] = 'text/html'
        cta_button = self.request.get( 'button' )

        if cta_button == "Save":
            firstname = self.request.get( 'firstname' )
            lastname = self.request.get( 'lastname' )
            if firstname == '' or lastname == '':
                message = "Firstname or lastname field CANNOT be empty"
                query_string = "?failed=" + message + "&firstname=" + firstname + "&lastname=" + lastname
                url = "/boards" + query_string
                self.redirect( url )
                return
            else:
                user = users.get_current_user()
                logged_user_key = ndb.Key( 'User', user.user_id() )
                logged_user = logged_user_key.get()
                logged_user.firstname = firstname
                logged_user.lastname = lastname
                logged_user.initials = self.getLoggedUserInitials( firstname + ' ' + lastname )
                logged_user.email = user.email()
                logged_user.put()
                message = "Thank you " + firstname.capitalize() + " " + lastname.capitalize() + " for updating your details."
                query_string = "?success=" + message + "&firstname=" + firstname + "&lastname=" + lastname
                url = "/boards" + query_string
                self.redirect( url )
                return
        else:
            pass


    def getLoggedUserInitials( self, username ):
        name_list = username.split(' ')
        word_count = len(name_list)
        if word_count == 1:
            return (name_list[0][0] + name_list[0][1]).upper()
        elif word_count > 1:
            return (name_list[0][0] + name_list[1][0]).upper()

    def getLoggedUserBoards(self, board_keys):
        logged_user_boards = []
        for board_key in board_keys:
            board = ndb.Key( 'Board', int(board_key) ).get()
            logged_user_boards.append( board )

        return logged_user_boards

app = webapp2.WSGIApplication(
    [
        webapp2.Route( r'/boards/<board_key:[^/]+>/<board_index:[^/]+>/<member_key:[^/]+>/remove-board-member', handler=RemoveMemberFromTaskBoard, name='remove-board-member'),
        webapp2.Route( r'/boards/<board_key:[^/]+>/<board_index:[^/]+>/<task_index:[^/]+>/delete-task', handler=DeleteTaskFromTaskBoard, name='delete-task'),
        webapp2.Route( r'/boards/<board_key:[^/]+>/<board_index:[^/]+>/<task_index:[^/]+>/edit-task', handler=EditTaskOnTaskBoard, name='edit-task'),
        webapp2.Route( r'/boards/<board_key:[^/]+>/<board_index:[^/]+>/<task_index:[^/]+>/unassign-task', handler=UnassignTaskInTaskBoard, name='unassign-task'),
        webapp2.Route( r'/boards/<board_key:[^/]+>/task-update-request', handler=TaskUpdateRequestProcess, name='task-request-services'),
        webapp2.Route( r'/boards/<board_key:[^/]+>/<board_index:[^/]+>/invite-member', handler=InviteMemberPage, name='invite-member'),
        webapp2.Route( r'/boards/<board_key:[^/]+>/<board_index:[^/]+>/add-task', handler=AddTaskPage, name='add-task'),
        webapp2.Route( r'/boards/<board_key:[^/]+>/<board_index:[^/]+>/edit-board-name', handler=EditBoardNamePage, name='edit-board-name'),
        webapp2.Route( r'/boards/<board_key:[^/]+>/<board_index:[^/]+>', handler=SelectedBoardPage, name='selected-board'),
        webapp2.Route( r'/boards', handler=MainPage, name='home'),
        webapp2.Route( r'/boards/create-board', handler=CreateBoardPage, name='create-board'),
        webapp2.Route( r'/', handler=RedirectHomeRoute, name='home-route-redirect'),
    ], debug = True
)
