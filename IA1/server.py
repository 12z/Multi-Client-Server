#!/usr/bin/env python

import select
import socket
import sys
import signal
import re
from os import environ

from communication import send, receive, Message, receive_name, send_address, send_message, BUFSIZ


class ChatServer(object):
    """ Simple chat server using select """

    def __init__(self, port=9999, backlog=5):
        self.clients = 0
        # Client map
        self.clientmap = {}
        # Output socket list
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('', port))
        print('Listening to port', port, '...')
        self.server.listen(backlog)
        # Trap keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)

    def sighandler(self, signum, frame):
        # Close the server
        print('Shutting down server...')
        # Close existing client sockets
        for o in self.outputs:
            o.close()

        self.server.close()

    def getname(self, client):

        # Return the printable name of the
        # client, given its socket...
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))

    def serve(self):

        if "TEST" in environ:
            inputs = [self.server]  # for testing on Win
        else:
            inputs = [self.server, sys.stdin]
        self.outputs = []

        kick_command = re.compile('^kick.*')

        running = 1

        while running:

            try:
                inputready, outputready, exceptready = select.select(inputs, self.outputs, [])
                # inputready, outputready, exceptready = select.select([self.server], self.outputs, [])
            except select.error as e:
                print(e)
                break
            except socket.error:
                break

            for s in inputready:

                if s == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print('chatserver: got connection %d from %s' % (client.fileno(), address))
                    # Read the login name
                    client_name = receive_name(client)

                    # Compute client name and send back
                    self.clients += 1
                    send_message(client, 'address', str(address[0]))
                    inputs.append(client)

                    self.clientmap[client] = (address, client_name)
                    # Send joining information to other clients
                    msg = '\n(Connected: New client (%d) from %s)' % (self.clients, self.getname(client))
                    for o in self.outputs:
                        send_message(o, 'text', msg)

                    self.outputs.append(client)

                elif s == sys.stdin:
                    # handle standard input
                    # print('got stdin event')
                    line = sys.stdin.readline().strip('\n')
                    # print('got input', line)
                    if line == 'list':
                        for client in self.clientmap:
                            # print('client')
                            print(self.getname(client))
                    elif kick_command.match(line):
                        name = line.split(' ')[1]
                        # print('here we kick', line.split(' ')[1])
                        for client in self.clientmap:
                            # print(self.getname(client))
                            if self.getname(client).split('@')[0] == name:
                                # print('got him')
                                # Send client leaving information to others
                                msg = '\n(Kicked: Client from %s)' % self.getname(client)
                                for o in self.outputs:
                                    send_message(o, 'text', msg)
                                self.clients -= 1
                                s.close()
                                inputs.remove(client)
                                self.outputs.remove(client)
                                del self.clientmap[client]
                                break
                else:
                    # handle all other sockets
                    try:
                        data = receive(s)
                        if data:
                            # Send as new client's message...
                            msg = '\n#[' + self.getname(s) + ']>> ' + data.text
                            # print('text: ', data.text)
                            # print('type: ', data.type)
                            # Send data to all except ourselves
                            for o in self.outputs:
                                if o != s:
                                    send_message(o, 'text', msg)
                        else:
                            print('chatserver: %d hung up' % s.fileno())
                            self.clients -= 1
                            s.close()
                            inputs.remove(s)
                            self.outputs.remove(s)
                            del self.clientmap[s]

                            # Send client leaving information to others
                            msg = '\n(Hung up: Client from %s)' % self.getname(s)
                            for o in self.outputs:
                                send_message(o, 'text', msg)

                    except socket.error:
                        # Remove
                        inputs.remove(s)
                        self.outputs.remove(s)
                        del self.clientmap[s]

        self.server.close()


if __name__ == "__main__":
    ChatServer().serve()
