import copy
from threading import Thread

import time

import ai
import humanplayer
import randomai
from go import Go

import json
import cherrypy

boardsize = 9

class Game:
    game = Go()
    ai1 = None
    ai2 = None

    history = []
    removedHistory = []

    def ai1turn(self, state):
        startingState = copy.deepcopy(state)
        move = self.ai1.turn(state, self.game)
        self.history.append({'player':self.ai1.player, 'state': startingState, 'move':move})
        return move

    def ai2turn(self, state):
        startingState = copy.deepcopy(state)
        move = self.ai2.turn(state, self.game)
        self.history.append({'player': self.ai2.player, 'state': startingState, 'move': move})
        return move

    def begin(self):
        self.game.begin(self.ai1turn, self.ai2turn, None, 'x', True, boardsize)

    @cherrypy.expose
    def back(self):
        last = self.history.pop()
        self.removedHistory.append(last)

        lastState = last['state']
        self.game.gsc = lastState
        self.game.gsf = lastState

        return json.dumps(lastState)

    @cherrypy.expose
    def next(self):
        last = self.removedHistory.pop()
        self.history.append(last)

        lastState = last['state']
        self.game.gsc = lastState
        self.game.gsf = lastState

        return json.dumps(lastState)

    @cherrypy.expose
    def move(self, x, y):
        self.ai1.makeMove(int(x), int(y))

        while True:
            time.sleep(.75)

            if self.game.currentPlayer == self.ai1.player:
                break

        return json.dumps(self.game.gsf)

    @cherrypy.expose
    def index(self):
        with open('go.js', 'r') as myfile:
            js = myfile.read()

        return """<html>
          <head>
            <script src="http://code.jquery.com/jquery-latest.min.js" type="text/javascript"></script>
          </head>
          <body style="width:500px">
            <div id="main">
                <img id="board" src="http://go.alamino.net/aprendajogargo/images/Blank_Go_board_9x9.png" width="500" height="500"/>


            </div>
            <div id="controls" style="display:flex">
                <button id="back" style="width:100%">Back</button>
                <button id="next" style="width:100%">Next</button>
            </div>
          </body>
          <footer><script type="text/javascript">{0}</script></footer>
        </html>
        """.format(js)


if __name__ == '__main__':
    import neuralai

    g = Game()

    g.ai1 = humanplayer.HumanPlayer('x', boardsize)
    g.ai2 = neuralai.NeuralAI('o', boardsize)

    Thread(target=g.begin, args=[]).start()
    cherrypy.quickstart(g)
