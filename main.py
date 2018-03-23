import game_client
import game_server
import os
import calc
import json
from logger import *

def clear_screen():
    os.system('cls')

def check(answer, cards):
    if answer == 'None': return True
    for elem in cards:
        if str(elem) not in answer:
            return False
    return True

def expect_answer(cards):
    if calc.calc_whether_get_24(list(cards)):
        return 24
    return None

def server_solve_questions(server):
    while not server.question_queue.empty():
        question = server.question_queue.get()
        print question
        answer = raw_input('answer: ')
        if answer == 'over':
            break
        else:
            if check(answer, question) and expect_answer(question) == eval(answer):
                server.score = server.score + 10
                server.update_player_score_to_clients(server.name, server.score)
                success_msg('right')
            else:
                warn_msg('wrong')

def client_solve_questions(client):
    clear_screen()
    normal_msg('waiting for server dispatch cards...')
    while not client.received_all_cards:pass
    while not client.question_queue.empty():
        question = client.question_queue.get()
        print question
        answer = raw_input('answer: ')
        if answer == 'over':
            client.leave_room()
            client.clear_question_queue()
            break
        else:
            if check(answer, question) and expect_answer(question) == eval(answer):
                client.score = client.score + 10
                client.update_score_to_server_message()
                success_msg('right')
            else:
                warn_msg('wrong')
    client.report_finished_questions()
    normal_msg('waiting others solve questions...')
    while not client.allow_next_round:pass

def game_round(question_numbers, server):
    clear_screen()
    normal_msg('WAITING CLIENTS JOIN, PRESS ANY WORD TO START GAME!')
    server.show_in_room_clients()
    raw_input('')
    server.allow_client_connect = False
    for i in range(question_numbers):
        cards = server.generate_numbers()
        if server.question_queue.full():
            server.question_queue.get()
        server.question_queue.put(cards)
        server.broadcast_dispatch_cards_msg(cards)
    server.mention_clients_all_cards_dispatched()
    server_solve_questions(server)
    if server.winner.score < server.score:
        server.winner.name = server.name
        server.winner.score = server.score
    normal_msg('waiting others finish questions...')
    while not server.are_all_clients_finished(): pass
    server.send_game_result_to_clients()
    normal_msg(server.winner.name + ' win the game with score ' + str(server.winner.score))
    return raw_input("game again? ") == 'y'


def create_server_env(logger, port, client_port):
    clear_screen()
    name = raw_input('Your name: ')
    return game_server.Server(logger, name, port, client_port)

def create_client_env(logger, port, server_port):
    clear_screen()
    name = raw_input('Your name: ')
    return game_client.Client(logger, name, port, server_port)

def server_start(server):
    num = input('number of questions each round: ')
    server.start_recv_msgs_from_clients()
    clear_screen()
    while game_round(num, server):
        server.reset()

def client_start(client):
    client.start_recv_msgs_from_server()
    client.search_room()
    client_solve_questions(client)
    while raw_input('continue? ') == 'y':
        client.reset()
        client_solve_questions(client)
    client.leave_room()

def read_config_file(filename):
    fd = open(filename, 'r')
    data = json.loads(fd.read())
    fd.close()
    return data

def prepare_game(endpoint):
    config_data = read_config_file('./config.ini')
    if 'server' == endpoint:
        return (config_data["server"]["log_file"], config_data["server"]["port"], config_data["client"]["port"])
    else:
        return (config_data["client"]["log_file"], config_data["client"]["port"], config_data["server"]["port"])
    

if __name__ == '__main__':
    res = raw_input('server/client: ')
    if res == 's':
        config_data = prepare_game('server')
        logger = Logger(config_data[0], True)
        server = create_server_env(logger, config_data[1], config_data[2])
        server_start(server)
        server.close_server()
    else:
        config_data = prepare_game('client')
        logger = Logger(config_data[0], True)
        client = create_client_env(logger, config_data[1], config_data[2])
        client_start(client)
        client.close_client()
