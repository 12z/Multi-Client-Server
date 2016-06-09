import pickle
import socket
import struct

marshall = pickle.dumps
unmarshall = pickle.loads

BUFSIZ = 1024


def send_name(sock, name):
    msg = Message()
    msg.type = 'name'
    msg.text = name
    send(sock, msg)


def receive_name(sock):
    msg = receive(sock)
    if msg.type == 'name':
        client_name = msg.text
    else:
        client_name = "Anonymous"
    return client_name


def send_address(sock, address):
    msg = Message()
    msg.type = 'address'
    msg.text = address
    send(sock, msg)


def receive_address(sock):
    msg = receive(sock)
    if msg.type == 'address':
        address = msg.text
    else:
        address = "Unknown_address"
    return address


def send_text(sock, text):
    msg = Message()
    msg.type = 'text'
    msg.text = text
    send(sock, msg)


def send_message(sock, msg_type, text):
    msg = Message()
    msg.type = msg_type
    msg.text = text
    send(sock, msg)


class Message:
    def __init__(self):
        self.text = ""
        self.type = ""


def send(channel, *args):
    buf = marshall(args)
    value = socket.htonl(len(buf))
    size = struct.pack("L", value)
    channel.send(size)
    channel.send(buf)


def receive(channel):
    size = struct.calcsize("L")
    size = channel.recv(size)
    try:
        size = socket.ntohl(struct.unpack("L", size)[0])
    except struct.error:
        return ''

    buf = ""

    while len(buf) < size:
        buf = channel.recv(size - len(buf))

    return unmarshall(buf)[0]
