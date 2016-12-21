import tornado.ioloop
import tornado.web
from tornado.log import enable_pretty_logging

import os.path
import bcrypt

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
        # Get the password info from the database
        info = dbhandler.getLogin(self.get_argument("user"))
        if info != False:
            pwd = info['password']
            salt = info['salt']
            pwd = bytes(pwd, "ascii")
            userpass = self.get_argument("password")
            hasheduserpass = hashPwd(userpass, salt)
            if hasheduserpass == pwd:
                self.set_secure_cookie("user", self.get_argument("user"))
                self.redirect("/")
            else:
                self.write("Incorrect user name or password")
        else:
            self.write("Incorrect user name or password")

# Class to handle logging out
class LogoutHandler(BaseHandler):
    def post(self):
        self.clear_cookie("user")
        self.redirect("/login")

# Function to hash a password supplied by the client and the salt retrieved
def hashPwd(pwd, salt):
    pwd = bytes(pwd, "ascii")
    salt = bytes(salt, "ascii")
    hashed = bcrypt.hashpw(pwd, salt)
    return(hashed)

# Initialise the application
enable_pretty_logging()
app = tornado.web.Application(
    [(r"/", RootHandler), (r"/login", LoginHandler), (r"/logout", LogoutHandler),],
    # Set the path where tornado will find the html templates
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    cookie_secret = "secret",
)

app.listen(8080)
# Start the asynchronous IO loop
tornado.ioloop.IOLoop.instance().start()
