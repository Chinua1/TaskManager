import webapp2

from board import Board

class RedirectHomeRoute( webapp2.RequestHandler ):
    def get( self ):
        self.redirect('/boards')
        return
