import socket as SK
from socket import socket
import time
from sys import exit
import copy
import threading


class ServerThread(threading.Thread):
    #def __init__(self, threadID, name, client_conn, server_conn,data):
    def __init__(self, client_socket, server_socket, data):
        threading.Thread.__init__(self)
        #self.threadID = threadID
        self.client_socket = client_socket
        self.server_socket = server_socket
        self.data = data
        #self.name = name

    def run(self):
        self.server_socket.send(self.data)
        response = self.server_socket.recv(1024) #recive the data from server
        self.client_socket.send(response)
        self.client_socket.close()
        return





class LoadBlancer():

    def __init__(self, local_ip, local_port, serv_dict, v=0 ):
        self.ip = local_ip
        self.port = local_port
        self.servers = serv_dict
        self.connections = {}
        self.lb_algorithm = v
        self.client_socket = None
        self.active_threads = []
        self.current_server_id = 0
        
    def run_lb(self):

        for s,i in self.servers.items():
            new_server_connection = socket(SK.AF_INET, SK.SOCK_STREAM)
            new_server_connection.connect((i, self.port))
            print " connected to: " + i
            self.connections[s] = new_server_connection

        self.client_socket = socket(SK.AF_INET, SK.SOCK_STREAM)
        self.client_socket.bind((self.ip, self.port))
        self.client_socket.listen(5)

        while True:
            new_client_socket, client_ip = client_socket.accept()
            #print to log

            request = new_client_socket.recv(1024)

            print "new mesage from: "+ client_ip
            print "    message is: "  + request

            # media_type = request[0]
            # proccess_time = int(request[1])
            best_server = self.pick_server(request) #TODO: routing algorithm return socket obj of selected server

            t = ServerThread(new_client_socket, best_server, data)
            active_threads.append(t)
            t.start()

        #for s, sock in self.connections.items():
        #    sock.close()
        #    if new_client_socket != None:
        #        new_client_socket.close()


    def pick_server(self, new_request):
        self.current_server_id = (self.current_server_id + 1) % 3
        print "current server is: " + self.current_server_id
        return self.connections[current_server_id]



if __name__ == '__main__':
    
    server_dict = {0:'192.168.0.101', 1:'192.168.0.102', 2:'192.168.0.103'}
    lb_IP = '10.0.0.1'
    lb = LoadBlancer(lb_IP, 80,server_dict)

    lb.run_lb()