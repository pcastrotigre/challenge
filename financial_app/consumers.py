import json
import logging
from .models import Room
from channels import Group
from channels import Channel
from lib import Rpc, RpcType, Consumer
from channels.sessions import channel_session, enforce_ordering
from channels.auth import channel_session_user, channel_session_user_from_http

log = logging.getLogger(__name__)


@channel_session_user_from_http
def ws_connect(message):
    # Extract the room from the message. This expects message.path to be of the
    # form /chat/{label}/, and finds a Room if the message path is applicable,
    # and if the Room exists. Otherwise, bails (meaning this is a some othersort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    try:
        prefix, label = message['path'].decode('ascii').strip('/').split('/')
        if prefix != 'chat':
            log.debug('invalid ws path=%s', message['path'])
            return
        room = Room.objects.get(label=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return

    log.debug('chat connect room=%s client=%s:%s',
        room.label, message['client'][0], message['client'][1])

    message.reply_channel.send({"accept": True})
    Group('chat-'+label, channel_layer=message.channel_layer).add(message.reply_channel)

    message.channel_session['room'] = room.label


@channel_session_user
def ws_receive(message):
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
    except KeyError:
        log.debug('no room in channel_session')
        return
    except Room.DoesNotExist:
        log.debug('recieved message, buy room does not exist label=%s', label)
        return

    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", data)
        return

    if 'message' not in data or 'username' not in data:
        log.debug("ws message unexpected format data=%s", data)
        return

    if data:
        Channel("chatmessages").send({
            "room": message.channel_session['room'],
            "message": data['message'],
            "username": data['username']
        })


@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
        Group('chat-'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, Room.DoesNotExist):
        pass




# Connected to chat-messages
def msg_consumer(message):
    label = message.content['room']
    room = Room.objects.get(label=label)

    msg = message.content['message']
    if msg.startswith("/"):
        ws = Consumer(msg)
        ws.run()
        response = { 
            'message': ws.get_message(),
            'timestamp': '',
            'username': 'system'
        }
    else:
        # Save to model
        m = room.messages.create(
            message=message.content['message'],
            username=message.content['username']
        )
        response = m.as_dict()
    # Broadcast to listening sockets
    Group("chat-%s" % room, channel_layer=message.channel_layer).send({
        "text": json.dumps(response),
    })

    return response
