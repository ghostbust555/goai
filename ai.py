import random
from random import shuffle
import go
import randomai

class AI:
    player = ''

    def __init__(self, player):
        self.player = player

    def score(self, gamestate):
        playerscore = 0
        enemyscore = 0

        for row in gamestate:
            for piece in row:
                if piece == self.player:
                    playerscore += 1
                elif piece != '-':
                    enemyscore += 1

        return playerscore, enemyscore


    def availableMoves(self, gamestate):
        available = []

        for x, row in gamestate:
            for y, piece in row:
                if piece == '-':
                    available.append([x, y])\

        return available

    def turn(self, gamestate):

        available = shuffle(self.availableMoves(gamestate))

        for move in available:
            ai1 = AI('x')
            ai2 = randomai.RandomAI('o')

            go.begin(lambda state: ai1.turn(state), lambda state: ai2.turn(state))


        # if gamestate[x][y] == "-":
        #     me, enemy = self.score(gamestate)
        #     if me + 12 < enemy:
        #         print("forfeit")
        #         return "forfeit"
        #
        #     return [y, x]
        # else:
        #     return self.turn(gamestate)
