import tornado.ioloop
import tornado.web

import os.path

import dbhandler

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

# Class to handle all requests to the root of the website URL
class RootHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        self.render("index.html")

# Class to handle logins
class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        email = self.get_argument("user")
        pwd = self.get_argument("password")
        self.clear_secure_cookie("user")
        self.set_secure_cookie("user", self.get_argument("user"))
        self.redirect("/")

# Class to handle logging out
class LogoutHandler(BaseHandler):
    def post(self):
        self.clear_cookie("user")
        self.redirect("/login")

# Initialise the application
app = tornado.web.Application(
    [(r"/", RootHandler), (r"/login", LoginHandler), (r"/logout", LogoutHandler),],
    # Set the path where tornado will find the html templates
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    cookie_secret = "secret",
)

app.listen(8080)
# Start the asynchronous IO loop
tornado.ioloop.IOLoop.instance().start()
