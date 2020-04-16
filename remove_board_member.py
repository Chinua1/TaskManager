import webapp2
import jinja2
import os
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from user import User
from board import Board

class RemoveMemberFromTaskBoard( webapp2.RequestHandler ):
    def get( self, board_key, board_index, member_key ):
        user = users.get_current_user()
        logged_user_key = ndb.Key( 'User', user.user_id() )
        logged_user = logged_user_key.get()
        board = ndb.Key('Board', int(board_key)).get()
        member = self.getMemberToBeRemove(User.query().fetch(), member_key)

        if not str(logged_user.key.id()) in board.members:
            message = 'Access Denied. Your membership has been revoked.'
            query_string = '?failed=' + message
            url = '/boards' + query_string
            self.redirect( url )

        for task in board.tasks:
            if task.assigned_to == member_key:
                task.assigned_to = ''
                task.completed = False
                task.completed_on = None
                task.high_lighted = True

        board.members.remove(member_key)
        member.boards.remove(str(board.key.id()))
        board.put()
        member.put()

        url = '/boards/' + board_key + '/' + board_index
        self.redirect(url)
        pass

    def getMemberToBeRemove(self, user_list, member_key):
        member = None
        for user in user_list:
            if str(user.key.id()) == member_key:
                member = user
        return member
