import tornado.ioloop
import tornado.web

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
        info = dbhandler.getLogin(self.get_argument("user"))
        print(self.get_argument("user"))
        pwd = info['password']
        salt = info['salt']
        pwd = bytes(pwd, "ascii")
        userpass = self.get_argument("password")
        hasheduserpass = hashPwd(userpass, salt)
        if hasheduserpass == pwd:
            self.set_secure_cookie("user", self.get_argument("user"))
            self.redirect("/")
        else:
            self.redirect("/login")

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
app = tornado.web.Application(
    [(r"/", RootHandler), (r"/login", LoginHandler), (r"/logout", LogoutHandler),],
    # Set the path where tornado will find the html templates
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    cookie_secret = "secret",
)

app.listen(8080)
# Start the asynchronous IO loop
tornado.ioloop.IOLoop.instance().start()
