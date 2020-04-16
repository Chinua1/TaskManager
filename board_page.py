import webapp2
import jinja2
import os
import datetime
import json

from datetime import datetime as dt_convert
from pytz import timezone
import pytz
import time

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from board import Board

from create_board import CreateBoardPage

start = os.path.dirname( __file__ )
rel_path = os.path.join(start, 'templates')
abs_path = os.path.realpath(rel_path)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class SelectedBoardPage( webapp2.RequestHandler ):
    def get( self, board_key, board_index ):
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

        board = ndb.Key( 'Board', int(board_key) ).get()

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
            'main_label': 'Personal Boards',
            'main_label_icon': "far fa-user fa-2x",
            'board': board,
            'board_members': self.getBoardMembers( User.query().fetch(), board.members ),
            'board_index': int(board_index),
            'members_json': json.dumps( [ dict(user.to_dict(), **dict(id=user.key.id())) for user in  User.query().fetch() ] ),
            'member_ids': json.dumps( board.members ),
            'dublintz': timezone('Europe/Dublin'),
            'utc': pytz.utc,
            'dt_convert': dt_convert,
            'time': time
        }

        template = JINJA_ENVIRONMENT.get_template( 'pages/board_page.html' )
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

    def getBoardMembers( self, user_list, member_key_list ):
        member_list = []

        for key in member_key_list:
            for user in user_list:
                if str(user.key.id()) == key:
                    member_list.append( user )

        return member_list
