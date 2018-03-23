import socket
import threading
import Queue
from logger import *

class UdpClient(object):
    def __init__(self, port):
        self.port = port
        self.msg_queue = Queue.Queue(100)
        self.ip = socket.gethostbyname(socket.gethostname())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind((self.ip, socket.htons(self.port)))
        except socket.error:
            error_msg('create socket error')
        self.udp_thread = threading.Thread(target = self.msg_receive_procedure, args = (self.sock,))

    def close(self):
        try:
            self.send_msg_to(self.target_end(self.ip, self.port), 'shutdown')
            self.udp_thread.join()
            self.sock.close()
        except socket.error:
            error_msg('close socket error')

    def msg_receive_procedure(self, sock):
        while True:
            (msg, addr) = sock.recvfrom(512)
            if 'shutdown' == msg:
                break
            if self.msg_queue.full():
                self.msg_queue.get()
            self.msg_queue.put(msg)

    def start_recv_msg_in_new_thread(self):
        try:
            self.udp_thread.start()
        except socket.error:
            error_msg('recv thread error')

    def send_msg_to(self, dest, msg):
        self.sock.sendto(msg, dest)

    def target_end(self, ip, port):
        return (ip, socket.htons(port))
