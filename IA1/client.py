#! /usr/bin/env python

import socket
import select
from os import environ

from communication import receive, receive_address, send_message


class ChatClient(object):
    def __init__(self, name, host='127.0.0.1', port=9999):
        self.name = name
        # Quit flag
        self.flag = False
        self.port = int(port)
        self.host = host
        # Initial prompt
        self.prompt = '[' + '@'.join((name, socket.gethostname().split('.')[0])) + ']> '
        # Connect to server at port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print('Connected to chat server@%d' % self.port)
            # Send my name...
            send_message(self.sock, 'name', self.name)
            # Set prompt with client's address
            self.prompt = '[' + '@'.join((self.name, receive_address(self.sock))) + ']> '
        except socket.error:
            print('Could not connect to chat server @%d' % self.port)
            sys.exit(1)

    def cmdloop(self):

        if "TEST" in environ:
            inputs = [self.sock]  # For testing on Win
        else:
            inputs = [0, self.sock]

        while not self.flag:
            try:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()

                # Wait for input from stdin & socket
                inputready, outputready, exceptrdy = select.select(inputs, [], [])

                for i in inputready:
                    if i == 0:
                        data = sys.stdin.readline().strip()
                        if data:
                            send_message(self.sock, 'text', data)
                    elif i == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print('Shutting down.')
                            self.flag = True
                            break
                        else:
                            if data.type == 'text':
                                sys.stdout.write(data.text + '\n')
                                sys.stdout.flush()
                            elif data.type == 'kick':
                                print('You were kicked by the server')
                                self.sock.close()
                                self.flag = True
                                break

            except KeyboardInterrupt:
                print('Interrupted.')
                self.sock.close()
                break


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        client = ChatClient(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    elif len(sys.argv) == 2:
        client = ChatClient(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 1:
        client = ChatClient(sys.argv[1])
    else:
        sys.exit('Usage: %s chatid host portno' % sys.argv[0])

    client.cmdloop()
