import json

class DispatchCardsMessage():
    def __init__(self, cards):
        self.id = 1
        self.card0 = cards[0]
        self.card1 = cards[1]
        self.card2 = cards[2]
        self.card3 = cards[3]
    def encode(self):
        return json.dumps({'id':self.id, 'card0':self.card0, 'card1':self.card1, 'card2':self.card2, 'card3':self.card3})

class UpadteScoreToServerMessage():
    def __init__(self, ip, name, score):
        self.id = 2
        self.name = name
        self.score = score
        self.ip = ip
    def encode(self):
        return json.dumps({'id':self.id, 'name':self.name, 'score':self.score, 'ip': self.ip})

class UpdatePlayerScoreToClients():
    def __init__(self, name, score):
        self.id = 3
        self.name = name
        self.score = score
    def encode(self):
        return json.dumps({'id':self.id, 'name':self.name, 'score':self.score})

class GetInRoomRequest():
    def __init__(self, ip, name):
        self.id = 4
        self.name = name
        self.ip = ip
    def encode(self):
        return json.dumps({'id':self.id, 'name':self.name, 'ip':self.ip})

class GetInRoomResponse():
    def __init__(self, ip, name, result):
        self.id = 5
        self.name = name
        self.ip = ip
        self.result = result
    def encode(self):
        return json.dumps({'id':self.id, 'name':self.name, 'ip':self.ip, 'result':self.result})

class LeaveRoomRequest():
    def __init__(self, ip, name):
        self.id = 6
        self.name = name
        self.ip = ip
    def encode(self):
        return json.dumps({'id':self.id, 'name':self.name, 'ip':self.ip})

class FinishQuestionsInd():
    def __init__(self, ip, name, score):
        self.id = 7
        self.name = name
        self.ip = ip
        self.score = score
    def encode(self):
        return json.dumps({'id':self.id, 'name':self.name, 'ip': self.ip, 'score':self.score})

class ReportGameResultMessage():
    def __init__(self, name, score):
        self.id = 8
        self.name = name
        self.score = score
    def encode(self):
        return json.dumps({'id':self.id, 'name':self.name, 'score':self.score})

class DispatchedAllCardsMessage():
    def __init__(self, ip):
        self.id = 9
        self.ip = ip
    def encode(self):
        return json.dumps({'id':self.id, 'ip':self.ip})