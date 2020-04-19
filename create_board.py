import webapp2
import jinja2
import os
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from board import Board

start = os.path.dirname( __file__ )
rel_path = os.path.join(start, 'templates')
abs_path = os.path.realpath(rel_path)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class CreateBoardPage( webapp2.RequestHandler ):
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
            'show_main_label': False,
            'main_label': '',
            'main_label_icon': "",
            'members_json': json.dumps( [] ),
            'member_ids': json.dumps( [] )
        }

        template = JINJA_ENVIRONMENT.get_template( 'pages/create_board.html' )
        self.response.write( template.render( template_values ) )
        return

    def post( self ):
        self.response.headers[ 'Content-Type' ] = 'text/html'
        cta_button = self.request.get( 'button' )
        user = users.get_current_user()
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()

        if cta_button == 'Create Board':
            board_title = self.request.get( 'board_title' )
            created_by = str(logged_user.key.id())
            created_at = str(datetime.datetime.now())

            if board_title:
                new_board = Board( title = board_title, created_by = created_by, created_at = created_at )
                new_board.members.append( created_by )
                board_key = new_board.put()

                board = board_key.get()
                logged_user.boards.append(str(board.key.id()))
                logged_user.put()

                if board:
                    message = board_title + " Board was successfully created."
                    query_string = "?success=" + message
                    url = "/boards" + query_string
                    self.redirect( url )
                    return
            else:
                message = "Board name is required to create a new board"
                query_string = "?failed=" + message
                url = "/boards/create-board" + query_string
                self.redirect( url )
                return


    def getLoggedUserInitials( self, username ):
        name_list = username.split(' ')
        word_count = len(name_list)
        if word_count == 1:
            return (name_list[0][0] + name_list[0][1]).upper()
        elif word_count > 1:
            return (name_list[0][0] + name_list[1][0]).upper()
