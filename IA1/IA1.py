import socketserver


class Handler(socketserver.BaseRequestHandler):
    # counter = 0

    def handle(self):
        while 1:
            data = self.request.recv(1024)
            if not data:
                break
            # self.data = self.data.strip()
            print(str(self.client_address[0]) + " wrote: ")
            print(data)
            self.request.send(data.upper())
        self.request.close()
        # # Echo the back to the client
        # data = self.request.recv(1024)
        # self.request.send(data)
        # print('Server received data', data)
        # # nonlocal self.counter += 1
        return


if __name__ == '__main__':
    import socket
    import threading

    address = ('localhost', 9999)  # let the kernel assign a port
    # server = socketserver.TCPServer(address, Handler)
    # ip, port = server.server_address  # what port was assigned?
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(address)
    s.listen()

    # t = threading.Thread(target=server.serve_forever)
    # t.setDaemon(True)  # don't hang on exit
    # t.start()

    test = input()
    # server.RequestHandlerClass.counter = 0

    # cond = 1
    # while cond == 1:
    #     pass

    # Clean up
    # server.shutdown()
    # server.socket.close()
