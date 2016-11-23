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

    def begin(self):
        self.game.begin(lambda state: self.ai1.turn(state, self.game), lambda state: self.ai2.turn(state, self.game), None, 'x', True, boardsize)

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
            <link href="/static/css/style.css" rel="stylesheet">
          </head>
          <body>
            <div id="main">
                <img id="board" src="http://go.alamino.net/aprendajogargo/images/Blank_Go_board_9x9.png" width="500" height="500"/>

                <script type="text/javascript">{0}</script>
            </div>
          </body>
        </html>
        """.format(js)


if __name__ == '__main__':
    import neuralai

    g = Game()

    g.ai1 = humanplayer.HumanPlayer('x', boardsize)
    g.ai2 = neuralai.NeuralAI('o', boardsize)

    Thread(target=g.begin, args=[]).start()
    cherrypy.quickstart(g)
