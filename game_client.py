import time
import threading
import Queue
import udp_client
from logger import *
from messages import *

class Client(udp_client.UdpClient):
    def __init__(self, logger = None, name = None, port = 2222, server_port = 1111):
        super(Client, self).__init__(port)
        self.logger = logger
        self.server_port = server_port
        self.question_queue = Queue.Queue(100)
        self.name = name
        self.score = 0
        self.server = None
        self.client_thread = threading.Thread(target = self.deal_received_msg)
        self.act_quit_game = False
        self.allow_next_round = False
        self.received_all_cards = False
        self.logger.log_msg('your address: ' + str(self.ip) + ':' + str(self.port))

    def clear_question_queue(self):
        while not self.question_queue.empty():
            self.question_queue.get()

    def deal_recv_cards_info(self, msg):
        cards = (msg['card0'], msg['card1'], msg['card2'], msg['card3'])
        self.question_queue.put(cards)
        self.logger.log_msg('client received cards: ' + str(cards))

    def deal_recv_player_score_info(self, msg):
        name = msg['name']
        score = msg['score']
        self.logger.log_msg(name + " : " + str(score))

    def deal_recv_get_in_room_resp(self, msg):
        if msg['result'] == 'accept':
            self.server = self.target_end(msg['ip'], self.server_port)
            self.logger.log_msg("access room success")
        else:
            self.logger.log_msg("access room fail")

    def deal_recv_report_game_result(self, msg):
        name = msg['name']
        score = msg['score']
        self.logger.log_msg(name + ' win the game with score ' + str(score))
        normal_msg(name + ' win the game with score ' + str(score))
        self.allow_next_round = True

    def deal_recv_all_cards_dispatched(self, msg):
        self.logger.log_msg("all questions received")
        self.received_all_cards = True

    def deal_received_msg(self):
        while not self.act_quit_game:
            if not self.msg_queue.empty():
                msg_str = self.msg_queue.get()
                msg = json.loads(msg_str)
                if msg['id'] == 1:
                    self.deal_recv_cards_info(msg)
                elif msg['id'] == 3:
                    self.deal_recv_player_score_info(msg)
                elif msg['id'] == 5:
                    self.deal_recv_get_in_room_resp(msg)
                elif msg['id'] == 8:
                    self.deal_recv_report_game_result(msg)
                elif msg['id'] == 9:
                    self.deal_recv_all_cards_dispatched(msg)
                else:
                    self.logger.log_msg('client received unknown message from server')
    
    def close_client(self):
        self.act_quit_game = True
        self.client_thread.join()
        self.close()

    def start_recv_msgs_from_server(self):
        self.start_recv_msg_in_new_thread()
        self.client_thread.start()
    
    def update_score_to_server_message(self):
        msg = UpadteScoreToServerMessage(self.ip, self.name, self.score)
        self.send_msg_to(self.server, msg.encode())

    def report_finished_questions(self):
        msg = FinishQuestionsInd(self.ip, self.name, self.score)
        self.send_msg_to(self.server, msg.encode())

    def search_room(self):
        msg = GetInRoomRequest(self.ip, self.name)
        target = self.target_end('<broadcast>', self.server_port)
        self.send_msg_to(target, msg.encode())
    
    def leave_room(self):
        msg = LeaveRoomRequest(self.ip, self.name)
        self.send_msg_to(self.server, msg.encode())

    def reset(self):
        self.score = 0
        self.allow_next_round = False
        self.received_all_cards = False
