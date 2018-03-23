import threading
import Queue
import udp_server
import random
from logger import *
from messages import *

class Winner:
    def __init__(self, name):
        self.score = 0
        self.name = ''

class ClientInfo(object):
    def __init__(self, name, score):
        self.name = name
        self.score = score
        self.is_finished_questions = False

class Server(udp_server.UdpServer):
    def __init__(self, logger = None, name = None, port = 1111, client_port = 2222):
        self.logger = logger
        self.client_port = client_port
        super(Server, self).__init__(port)
        self.question_queue = Queue.Queue(100)
        self.name = name
        self.score = 0
        self.clients = dict()
        self.act_quit_game = False
        self.allow_client_connect = True
        self.winner = Winner(self.name)
        self.server_thread = threading.Thread(target = self.deal_received_msg)
        self.logger.log_msg('your address: ' + str(self.ip) + ':' + str(self.port))

    def generate_numbers(self):
        nums = (random.randint(1, 13), random.randint(1, 13), random.randint(1, 13), random.randint(1, 13))
        self.logger.log_msg('generate cards: ' + str(nums))
        return nums

    def clear_question_queue(self):
        while not self.question_queue.empty():
            self.question_queue.get()

    def deal_recv_score_submit_from_client(self, msg):
        name = msg['name']
        ip = msg['ip']
        score = msg['score']
        if score > self.winner.score:
            self.winner.score = score
            self.winner.name = name
        if ip in self.clients:
            self.logger.log_msg('the score of ' + name + ' up to ' + str(score))
            self.clients[ip].score = score
            self.update_player_score_to_clients(name, score)
        else:
            self.logger.log_msg('received an unknow person update his/her score')

    def deal_client_get_in_room(self, msg):
        name = msg['name']
        ip = msg['ip']
        if not self.allow_client_connect:
            self.logger.log_msg(name + ' ' + ip + ' try to access room when you are gameing, and we reject')
            self.send_get_in_room_resp(self.target_end(ip, self.client_port), 'reject')
            return
        if ip in self.clients:
            self.logger.log_msg(name + " had already in room, shouldn't access twice")
            return
        self.clients[ip] = ClientInfo(name, 0)
        self.send_get_in_room_resp(self.target_end(ip, self.client_port), 'accept')
        self.logger.log_msg(name + ' get in room')
        normal_msg(name + ' enter room')

    def deal_client_leave_room(self, msg):
        name = msg['name']
        ip = msg['ip']
        if ip in self.clients:
            self.logger.log_msg(name + ' leaved room')
            del self.clients[ip]
            normal_msg(name + ' leave')
        else:
            self.logger.log_msg('an unknown man ' + name + ' leaved room')
    
    def deal_recv_client_finish_questions_ind(self, msg):
        ip = msg['ip']
        name = msg['name']
        score = msg['score']
        if ip in self.clients:
            self.logger.log_msg(name + ' finished all questions with score ' + str(score))
            self.clients[ip].is_finished_questions = True

    def deal_received_msg(self):
        while not self.act_quit_game:
            if not self.msg_queue.empty():
                msg_str = self.msg_queue.get()
                msg = json.loads(msg_str)
                if msg['id'] == 2:
                    self.deal_recv_score_submit_from_client(msg)
                elif msg['id'] == 4:
                    self.deal_client_get_in_room(msg)
                elif msg['id'] == 6:
                    self.deal_client_leave_room(msg)
                elif msg['id'] == 7:
                    self.deal_recv_client_finish_questions_ind(msg)
                else:
                    self.logger.log_msg('received a unknown message from client')
    
    def start_recv_msgs_from_clients(self):
        self.start_recv_msg_in_new_thread()
        self.server_thread.start()

    def broadcast_dispatch_cards_msg(self, cards):
        msg = DispatchCardsMessage(cards)
        for item in self.clients:
            self.send_msg_to(self.target_end(item, self.client_port), msg.encode())
    
    def send_get_in_room_resp(self, target, result):
        msg = GetInRoomResponse(self.ip, self.name, result)
        self.send_msg_to(target, msg.encode())

    def update_player_score_to_clients(self, name, score):
        msg = UpdatePlayerScoreToClients(name, score)
        for item in self.clients:
            self.send_msg_to(self.target_end(item, self.client_port), msg.encode())

    def mention_clients_all_cards_dispatched(self):
        msg = DispatchedAllCardsMessage(self.ip)
        for item in self.clients:
            self.send_msg_to(self.target_end(item, self.client_port), msg.encode())

    def send_game_result_to_clients(self):
        msg = ReportGameResultMessage(self.winner.name, self.winner.score)
        for item in self.clients:
            self.send_msg_to(self.target_end(item, self.client_port), msg.encode())

    def are_all_clients_finished(self):
        for ip in self.clients:
            if self.clients[ip].is_finished_questions == False:
                return False
        return True

    def reset(self):
        self.clear_question_queue()
        self.score = 0
        self.winner.score = 0
        self.winner.name = self.name
        self.allow_client_connect = True
        for ip in self.clients:
            self.clients[ip].is_finished_questions = False
            self.clients[ip].score = 0

    def close_server(self):
        self.act_quit_game = True
        self.server_thread.join()
        self.close()

    def show_in_room_clients(self):
        for ip in self.clients:
            normal_msg(self.clients[ip].name + ' already in room')
