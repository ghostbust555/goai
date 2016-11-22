import ai
import randomai
from go import Go

import cherrypy

boardsize = 9


class Game:
    game = Go()

    def main(self):
        randomAi = randomai.RandomAI('x', boardsize)
        neuralAi = neuralai.NeuralAI('x', boardsize)
        ai2 = ai.AI('o', boardsize)

        self.game.begin(lambda state: neuralAi.turn(state, self.game), lambda state: ai2.turn(state, self.game), None, 'x', True, boardsize)

    @cherrypy.expose
    def move(self, x, y):
        return "ok"

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
    cherrypy.quickstart(g)
    #g.main()
