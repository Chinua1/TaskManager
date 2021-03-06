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

start = os.path.dirname( __file__ )
rel_path = os.path.join(start, 'templates')
abs_path = os.path.realpath(rel_path)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader( abs_path ),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class InviteMemberPage( webapp2.RequestHandler ):
    def get( self, board_key, board_index):
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
            'main_label': 'Invite Member',
            'main_label_icon': "fas fa-user-plus fa-2x",
            'board_key': board_key,
            'users': self.getNonBoardMemberList(User.query().fetch(), ndb.Key("Board", int(board_key)).get()),
            'board_index': int(board_index),
            'members_json': json.dumps( [] ),
            'member_ids': json.dumps( [] )
        }

        template = JINJA_ENVIRONMENT.get_template( 'pages/invite_member.html' )
        self.response.write( template.render( template_values ) )
        return


    def post( self, board_key, board_index ):
        self.response.headers[ 'Content-Type' ] = 'text/html'
        message = ""
        query_string = ""
        url = ""

        member_key = self.request.get('member_key')

        if member_key == "":
            message = "Choose a member to add from the dropdown list"
            query_string = "?failed=" + message
            url = '/boards/' + board_key + '/' + board_index + '/invite-member' + query_string
            self.redirect( url )
            return
        else:
            board = ndb.Key( 'Board', int(board_key) ).get()
            if member_key in board.members:
                pass
            else:
                board.members.append(member_key)
                board.put()
                member = self.getProspectiveMember(User.query().fetch(), member_key)
                member.boards.append(str(board.key.id()))
                member.put()
                message = "Member was successfully added."
                query_string = "?success=" + message

            url = '/boards/' + board_key + '/' + board_index + query_string

        self.redirect( url )
        return

    def getLoggedUserInitials( self, username ):
        name_list = username.split(' ')
        word_count = len(name_list)
        if word_count == 1:
            return (name_list[0][0] + name_list[0][1]).upper()
        elif word_count > 1:
            return (name_list[0][0] + name_list[1][0]).upper()

    def getProspectiveMember(self, user_list, member_key):
        member = None
        for user in user_list:
            if str(user.key.id()) == member_key:
                member = user
        return member

    def getNonBoardMemberList( self, user_list, board):
        non_member_list = []
        for user in user_list:
            non_member = True
            for key in board.members:
                if str(user.key.id()) == key:
                    non_member = False
            if non_member:
                non_member_list.append(user)
        return non_member_list
