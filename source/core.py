import tornado.ioloop
import tornado.web

import os.path

# Class to handle all requests to the root of the website URL
class RootHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

# Initialise the application
app = tornado.web.Application(
    [(r"/", RootHandler),],
    # Set the path where tornado will find the html templates
    template_path = os.path.join(os.path.dirname(__file__), "templates"),
)

app.listen(8080)
# Start the asynchronous IO loop
tornado.ioloop.IOLoop.instance().start()
