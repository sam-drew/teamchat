import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.log import enable_pretty_logging
import logging
import os.path
import bcrypt

import dbhandler

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("email")

# Class to handle all requests to the root of the website URL
class RootHandler(BaseHandler):
    def get(self):
        self.render("index.html")

# Class to handle logins
class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html", message = "")

    def post(self):
        # Get the password info from the database
        info = dbhandler.getLogin(self.get_argument("email"))
        if info != False:
            pwd = info['password']
            salt = info['salt']
            pwd = bytes(pwd, "ascii")
            userpass = self.get_argument("password")
            hasheduserpass = hashPwd(userpass, salt)
            if hasheduserpass == pwd:
                self.set_secure_cookie("email", self.get_argument("email"))
                self.redirect("/home")
            else:
                self.render("login.html", message = "bad info")
        else:
            self.render("login.html", message = "bad info")

# Class to handle logging out
class LogoutHandler(BaseHandler):
    def post(self):
        self.clear_cookie("email")
        self.redirect("/")

# Class to handle requests to the /home uri
class HomeHandler(BaseHandler):
    def get(self):
        if not self.get_secure_cookie("email"):
            self.redirect("/login")
            return
        else:
            userEmail = (self.get_secure_cookie("email").decode("utf-8"))
            chatNames = dbhandler.getChatNameID(userEmail)
            if dbhandler.checkAdmin(dbhandler.getUserID(userEmail)['ID']) == True:
                self.render("homeAdmin.html", email = userEmail, chats = chatNames, alerts = [])
            else:
                self.render("home.html", email = userEmail, chats = chatNames)

class NewUserHandler(BaseHandler):
    def get(self):
        self.redirect("/home")

    def post(self):
        info = []
        for argument in ["email1", "email2", "userName", "userPass1", "userPass2"]:
            info.append(self.get_argument(argument))
        logging.info("Attempt to add new user: {0}".format(info))
        userEmail = (self.get_secure_cookie("email").decode("utf-8"))
        chatNames = dbhandler.getChatNameID(userEmail)
        alerts = []
        if self.get_argument("email1") != self.get_argument("email2"):
            alerts.append("Emails do not match")
            if self.get_argument("userPass1") != self.get_argument("userPass2"):
                alerts.append("Passwords do not match")
                logging.info("Failed to add new user; neither match")
                self.render("homeAdmin.html", email = userEmail, chats = chatNames, alerts = alerts)
            else:
                self.render("homeAdmin.html", email = userEmail, chats = chatNames, alerts = alerts)
                logging.info("Failed to add new user; emails don't match")
        elif self.get_argument("userPass1") != self.get_argument("userPass2"):
            alerts.append("Passwords do not match")
            logging.info("Failed to add new user; pwds don't match")
            self.render("homeAdmin.html", email = userEmail, chats = chatNames, alerts = alerts)
        else:
            userID = dbhandler.getUserID(userEmail)['ID']
            newEmail = self.get_argument("email1")
            name = self.get_argument("userName")
            salt = (bcrypt.gensalt()).decode("utf-8")
            password = (hashPwd(self.get_argument("userPass1"), salt)).decode("utf-8")
            returnValue = dbhandler.addNewUser(userID, newEmail, name, password, salt)
            if returnValue == True:
                self.render("homeAdmin.html", email = userEmail, chats = chatNames, alerts = ["Success",])
                logging.info("Added new user successfully")
            else:
                logging.error("Failed to add a new user")
                logging.error(returnValue)
                self.render("homeAdmin.html", email = userEmail, chats = chatNames, alerts = ["Failed to add new user",])


# Class to handle all url's beginning with "/url/".
class ChatHandler(BaseHandler):
    def get(self, link):
        userEmail = self.get_secure_cookie("email")
        if userEmail != None:
            userEmail = userEmail.decode("utf-8")
            if dbhandler.checkEmail(userEmail) == True:
                userID = dbhandler.getUserID(userEmail)['ID']
                if dbhandler.checkChatPrivileges(userID, link) != False:
                    messageList = dbhandler.getRecentMessages(link)
                    isAdmin = dbhandler.checkChatPrivileges(userID, link)
                    if messageList != False:
                        messageList.reverse()
                        for m in messageList:
                            userName = dbhandler.getUserName(m['memberID'])
                            m['uName'] = userName['name']
                    else:
                        messageList = []
                    if isAdmin != False:
                        self.render("chatAdmin.html", messages = messageList, chatname = link)
                    else:
                        self.render("chat.html", messages = messageList, chatname = link)
                else:
                    self.redirect("/home")
            else:
                self.redirect("/")
        else:
            self.redirect("/")

# Class to handle the WebSocket connections.
class WSocketHandler(tornado.websocket.WebSocketHandler, BaseHandler):
    connectedClients = {}

    def open(self, url):
        self.url = url
        self.chatID = WSocketHandler.stripUrl(url)
        if self.chatID in WSocketHandler.connectedClients:
            WSocketHandler.connectedClients[self.chatID].append(self)
        else:
            WSocketHandler.connectedClients[self.chatID] = [self,]
        logging.info("New Connection {0}, to chatID {1}".format(self, self.chatID))

    def on_close(self):
        WSocketHandler.connectedClients[self.chatID].remove(self)
        logging.info("Disconnect {0}, from chatID {1}".format(self, self.chatID))

    def on_message(self, message):
        userEmail = self.get_secure_cookie("email")
        userEmail = userEmail.decode("utf-8")
        userID = dbhandler.getUserID(userEmail)['ID']
#        logging.warn(("USERNAME on_message:", userName))
#        logging.warn(("USERID on_message:", userID))
        if dbhandler.checkChatPrivileges(userID, self.chatID) != False:
            message = tornado.escape.json_decode(message)['body']
#            logging.warn(message)
            messageID = dbhandler.setMessage(userID, self.chatID, message)
#            logging.info(("MESSAGE ID: ", messageID))
            if isinstance(messageID, int) == True:
                logging.info("Successfully saved message")
                newChatMessage = {
                'id': messageID,
                'content': message,
                'uName': dbhandler.getUserNameFromID(userID)['name']
                }
                newChatMessage['html'] = tornado.escape.to_basestring(
                self.render_string('newMessage.html', message = newChatMessage)
                )
#                logging.info(newChatMessage)
#                logging.info(self.chatID)
                WSocketHandler.sendMessages(newChatMessage, self.chatID)
            else:
                logging.error("Error saving message")
        else:
            logging.warn("Message attempt with incorrect privileges. User: {0}, Chat:{1}".format(userID, self.chatID))

    @classmethod
    def sendMessages(cls, message, chat):
        for user in WSocketHandler.connectedClients[chat]:
            try:
                user.write_message(message)
#                logging.info(("User name passed to sendMessages:", message['uName']))
                logging.info("Sent a message")
            except:
                logging.error("Failed to send a message")

    @classmethod
    def stripUrl(cls, url):
        splitString = url.rsplit("/", 1)
        return(splitString[(len(splitString ) - 1)])

# Function to hash a password supplied by the client and the salt retrieved
def hashPwd(pwd, salt):
    pwd = bytes(pwd, "ascii")
    salt = bytes(salt, "ascii")
    hashed = bcrypt.hashpw(pwd, salt)
    return(hashed)

# Initialise the application
enable_pretty_logging()
app = tornado.web.Application(
    [(r"/", RootHandler), (r"/login", LoginHandler), (r"/logout", LogoutHandler),
     (r"/home", HomeHandler), (r"/chat/(.*)", ChatHandler), (r"/socket/(.*)", WSocketHandler),
     (r"/a/newUser", NewUserHandler),],
    # Set the path where tornado will find the html templates
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    cookie_secret = "secret",
    xsrf_cookies = True,
)

app.listen(8080)
# Start the asynchronous IO loop
tornado.ioloop.IOLoop.instance().start()
