import socket as SK
from socket import socket
import time
from sys import exit
import sys
import copy
import threading


class ServerThread(threading.Thread):
    def __init__(self, client_socket, server_socket, data):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.server_socket = server_socket
        self.data = data

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
        self.server_jobs = {}
        for s in self.servers:
            self.server_jobs[s] = 0
        self.last_rec_time = 0
        self.weight_db = {'V' : [1,1,3], 'P' : [1,1,2], 'M': [2,2,1]}

        
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
            new_client_socket, client_ip = self.client_socket.accept()
            request = new_client_socket.recv(1024)
            print "new mesage from: "+ client_ip[0]
            print "    message is: "  + request
            best_server = self.pick_server(request)
            t = ServerThread(new_client_socket, best_server, request)
            self.active_threads.append(t)
            t.start()


    def get_correct_time(self, rec):
        c = rec[0]
        t = int(rec[1])
        real_weights = {0: self.server_jobs[0] + t*self.weight_db[c][0],
                        1: self.server_jobs[1] + t*self.weight_db[c][1],
                        2: self.server_jobs[2] + t*self.weight_db[c][2]}
        return real_weights


    def smart_rout(self, rec):
        new_t = time.clock()
        time_delta = new_t - self.last_rec_time
        for s,t  in self.server_jobs.items():
            new_jobs = max (t - time_delta,0)
            self.server_jobs[s] = new_jobs

        temp_jobs = self.get_correct_time(rec)
        min = sys.maxint
        best = 0
        for s,t in temp_jobs.items():
            if t < min:
                min = t
                best = s

        self.last_rec_time = new_t
        self.server_jobs[best] = min
        return best



    def pick_server(self, new_request):

        if self.lb_algorithm == 0:
            self.current_server_id = (self.current_server_id + 1) % 3
            print "current server is: " + str(self.current_server_id)
            return self.connections[self.current_server_id]
        elif self.lb_algorithm == 1:
            self.current_server_id = self.smart_rout(new_request)
            print "current server is: " + str(self.current_server_id)
            return self.connections[self.current_server_id]







if __name__ == '__main__':
    server_dict = {0:'192.168.0.101', 1:'192.168.0.102', 2:'192.168.0.103'}
    lb_IP = '10.0.0.1'
    lb = LoadBlancer(lb_IP, 80,server_dict, 1)
    lb.run_lb()