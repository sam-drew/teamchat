import tornado.ioloop
import tornado.web
import tornado.websocket

import os.path

class RootHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")

app = tornado.web.Application(
    [(r"/", RootHandler),],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
)

app.listen(8080)
tornado.ioloop.IOLoop.instance().start()
