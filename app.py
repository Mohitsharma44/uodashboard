from tornado import websocket, web, ioloop
import json

# list of clients to push the data to
clients = []

class IndexHandler(web.RequestHandler):
    """
    Class to handle the landing page
    """
    pass


class RealtimeHandler(websocket.WebSocketHandler):
    """
    Class to handle the sockets
    """
    def check_origin(self):
        """
        Accept all cross-origin traffic
        """
        return True

    def open(self):
        self.write_message("Socket opened")

    def on_message(self, message):
        print("Message Recieved: " + message)

    def on_close(self):
        print("Socket closed")


class ApiHandler(web.RequestHandler):
    """
    Class to handle the data received
    """
    pass


app = web.Application(
    [
        (r'/realtime', RealtimeHandler)
    ], debug=True,
)

if __name__ == "__main__":
    app.listen(8888)
    ioloop.IOLoop.instance().start()
