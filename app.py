
import os
import json
import time
import base64
from io import StringIO
from tornado import websocket, web, ioloop, gen, escape

# list of clients to push the data to
clients = []

class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")


class AudubonHandler(BaseHandler):
    """
    Class to handle the landing page
    """
    @web.asynchronous
    @web.authenticated
    def get(self):
        name = escape.xhtml_escape(self.current_user)
        self.render("audubon.html",
                    title="UO Live",
                    cam1="D6",
                    cam2="D9")

        
class HadiveHandler(BaseHandler):
    """
    Class to handle the Hadive project page
    """
    @web.asynchronous
    @web.authenticated
    def get(self):
        name = escape.xhtml_escape(self.current_user)
        self.render("hadive.html",
                    title="HaDiVe")

class IndexHandler(web.RequestHandler):
    """
    Class to handle index page
    """
    def get(self):
        self.render("index.html", title="index")


class PubHandler(web.RequestHandler):
    """
    Class to handle index page
    """
    def get(self):
        self.render("UOpublications.html", title="UO publications")

class comingsoonHandler(web.RequestHandler):
    """
    Class to handle index page
    """
    def get(self):
        self.render("comingsoon.html", title="comint soon")

class LoginHandler(BaseHandler):
    def get(self):
        try:
            if self.get_current_user():
                self.redirect(self.get_argument('next', '/'))
                return
            error_msg = self.get_argument("error")
        except:
            error_msg = ""
        self.render("login.html", errormessage=error_msg)

    def post(self):
        username = self.get_argument("username", "")
        passwd = self.get_argument("password", "")
        # __TODO: Steps for Authentication
        if username == "mohit":
            self.set_current_user(username)
            self.redirect(self.request.headers.get('referer', '/'))
            #self.redirect(self.get_argument("next", u"/"))
        else:
            error_msg = u"?error=" + escape.url_escape("Login incorrect")
            self.redirect(u"/login" + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", escape.json_encode(user))
        else:
            self.clear_cookie("user")


class LogoutHandler(BaseHandler):
    """
    Class to handle logout
    """
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", u"/"))


class RealtimeHandler(websocket.WebSocketHandler):
    """
    Class to handle the sockets
    """
    def check_origin(self, origin):
        """
        Accept all cross-origin traffic
        """
        return True
    def open(self):
        if self.get_secure_cookie("user"):
            self.write_message("Socket opened")
            if not self in clients:
                clients.append(self)
        else:
            self.close(code=401, reason="Unauthorized")
            return

    def on_message(self, message):
        print("Message Recieved: " + message)

    def on_close(self):
        if self in clients:
            clients.remove(self)
        print("Socket closed")


class ApiHandler(web.RequestHandler):
    """
    Class to handle the data received
    """
    def get(self):
        pass

    def post(self, *args):
        # Got an image? Push it to the clients
        #print(self.request.body)
        self.file1 = self.request.files['file1'][0]
        with open("test.png", "wb") as fh:
            fh.write(self.file1.body)
        self.orig_fname = self.file1['filename']
        print("Got :"+str(self.orig_fname))
        data = {"cam_name": str(self.request.headers['cam_name']),
                "fname": str(self.orig_fname),
                "updatetime": str(time.strftime("%c")),
                "img": str(base64.b64encode(self.file1['body']))
        }
        for client in clients:
            client.write_message(data)
        # Send OK to the uploader and close
        self.write("OK")


settings = {
    'login_url': '/login',
    'cookie_secret': 'L8LwECiNRxq2N0N2eGxx9MZlrpmuMEimlydNX/vt1LM=',
    'template_path': 'templates/',
    'compiled_template_cache': 'False',
    'debug': True,
    'static_path': os.path.join(os.path.dirname(__file__), "static")
}

app = web.Application(
    [
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler),
        (r'/realtime', RealtimeHandler),
        (r'/upload', ApiHandler),
        (r'/index', IndexHandler),
        (r'/', IndexHandler),
        (r'/uopublications', PubHandler),
        (r'/comingsoon', comingsoonHandler),        
        (r'/projects/audubon', AudubonHandler),
        (r'/projects/hadive', HadiveHandler),
    ],
    **settings,
)

if __name__ == "__main__":
    app.listen(9998)
    ioloop.IOLoop.instance().start()
