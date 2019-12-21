import os  # TODO problem???
import sys
from socket import *


# do i need here singleton??


class Server:

    def __init__(self):
        self.file_name = "/"
        self.port = 8080  # defulte value
        self.server = socket(AF_INET, SOCK_STREAM)
        self.path = ""

    # connect to the client- preform bind operation to ip and port
    def connect(self):
        server_ip = '127.0.0.1'
        self.server.bind((server_ip, int(self.port)))
        self.server.listen(5)

    # sends the data directly
    def sendR(self):
        client_socket, client_address = self.server.accept()
        self.send(self.file_name.encode())

    # sends the data binary
    def sendB(self):
        while True:
            client_socket, client_address = self.server.accept()
            f = open(self.file_name, 'rb')
            f.seek(0)
            payload = f.read(1024)
            while payload:
                client_socket.sendall(payload)
                payload = f.read(1024)
            f.close()

    #  TODO- what server returns
    def prosseceClinetOutput(self):
        pass

    # connect and down load the file
    def download(self):
        # start connection
        self.connect()
        # init all files in base folder to list
        data = os.listdir(str(self.path))
        # if there such file- ask if it jpg/ico- send binary, otherwise send the file as is
        if self.file_name in data:
            # check if the postfix is jpg/ico
            if "jpg" in self.file_name or "ico" in self.file_name:
                # send binary
                self.sendB()
                # print the data
                self.prosseceClinetOutput()
            else:
                # send diractly
                self.sendR()
                # print the data
                self.prosseceClinetOutput()

    # create a legal path for download
    def create_path(self, input_list, size):
        path = ""
        if input_list[0] is "/":
            path = "/"
            return "./files" + path
        path_list = input_list[1:size - 1]
        for i in path_list:  # init path
            path += i
            path += "/"
        path = path[:len(self.path) - 1]  # get rid of the last "/"
        return "./files/" + path

    # prossece the input - init the file name, port and path
    def prosseceServerInput(self, filename):

        input_list = filename.split('/')  # ["8080","a","oh_no.jpg" ]
        size = len(input_list)
        # init port from input
        default_port = 8080
        if isinstance(int(input_list[0]), int):  # init the port
            self.port = input_list[0]
        # init path from input
        self.path = self.create_path(input_list, size)
        # init file name from input
        if self.path is "/":
            self.file_name = "‫‪index.html‬‬"
            return self.file_name
        else:
            self.file_name = input_list[size - 1]
            return self.file_name  # return file name


if __name__ == "__main__":
    # input = sys.argv[0]  # for example: localhost:8080/a/oh_no.jpg----> i will recive 8080/a/oh_no.jpg
    input = "8080/a/oh_no.jpg"
    server = Server()
    file_name = server.prosseceServerInput(input)
    server.download()
