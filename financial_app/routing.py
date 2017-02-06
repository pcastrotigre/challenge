# from channels.staticfiles import StaticFilesConsumer
from . import consumers
from channels.routing import route

channel_routing = [
    route("websocket.receive", consumers.ws_receive),
    route("websocket.connect", consumers.ws_connect),
    route("websocket.disconnect", consumers.ws_disconnect),
    route("chatmessages", consumers.msg_consumer),
]