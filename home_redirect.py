import webapp2

class RedirectHomeRoute( webapp2.RequestHandler ):
    def get( self ):
        self.redirect('/boards')
        return
