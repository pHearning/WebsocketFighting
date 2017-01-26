from tornado import httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import json
import time
import random
'''
This is a simple Websocket Echo server that uses the Tornado websocket handler.
Please run `pip install tornado` with python of version 2.7.9 or greater to install tornado.
This program will echo back the reverse of whatever it recieves.
Messages are output to the terminal for debuggin purposes.
'''



class Player():
    def __init__(self, name):
        self.hp = 20
        self.name = "red"
        self.power = 1
        self.last_move = ""
        self.dodge = 10
        self.strength = 1

    def lose_hp(self, amount):
        self.hp -= amount

    def attack(self, move, opponent_move):
        self.last_move = move.lower()
        if move.lower() == 'kick':
            if opponent_move == 'block':
                return 0
            else:
                return random.randint(1,4)*self.strength
        elif move.lower() == 'punch':
            if opponent_move == 'block':
                return random.randint(1,2)*self.strength
            else:
                return random.randint(1,3)*self.strength
        elif move.lower() == 'block':
            return 0

    def defence(self, amount):
        if random.randint(0, 100) > self.dodge:
            self.lose_hp(amount)
            return amount
        else:
            return 0
        

class Match():

    def __init__(self):
        self.red = Player('red')
        self.blue = Player('blue')
        self.turn = random.choice(['red', 'blue'])
        self.running = True

    def round(self, active_player, move):

        if active_player == 'red' and self.turn == 'red':
            self.turn = 'blue'
            damage = self.blue.defence(self.red.attack(move,self.blue.last_move))
            if self.blue.hp <= 0:
                self.running = False
                return 'Blue is dead Red wins'

            else:
                return json.dumps({"message": "red hit blue with {0} for {1} damage.".format(move, str(damage)), "red_hp": self.red.hp, "blue_hp": self.blue.hp, "move":"{0}".format(move), "turn": "blue"})

        elif active_player == 'blue' and self.turn == 'blue':
            self.turn = 'red'
            damage = self.red.defence(self.blue.attack(move,self.red.last_move))
            if self.red.hp <= 0:
                self.running = False
                return 'Red is dead Blue wins'

            else:
                return json.dumps({"message": "blue hit red with {0} for {1} damage.".format(move, str(damage)), "red_hp": self.red.hp, "blue_hp": self.blue.hp, "move":"{0}".format(move), "turn": "red"})

        else:
            return 'Please wait for your turn'


class WSHandler(tornado.websocket.WebSocketHandler):
    connections = set()
    def __init__(self, *args, **kwargs):
        game = Match()
        super(WSHandler, self).__init__(*args, **kwargs)

    def open(self):
        self.connections.add(self)
        print('new connection')
        [con.write_message(json.dumps({"message":"A new player has join the game", "turn":game.turn})) for con in self.connections]

    def on_message(self, message):
        message = json.loads(message)
        player = message["player"]
        move = message["move"]
        
        # Make a turn in the game
        response = game.round(player, move)
        time.sleep(2)
        [con.write_message(response) for con in self.connections]
        if not game.running:
            self.close()
    def on_close(self):
        self.connections.remove(self)
        print('connection closed')

    def check_origin(self, origin):
        return True

application = tornado.web.Application([
    (r'/ws', WSHandler),
])

def main():
    global game
    game = Match()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888, address="10.161.124.143")
    myIP = socket.gethostbyname(socket.gethostname())
    print(game.turn)
    print ('*** Websocket Server Started at {0}***'.format(myIP))
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
