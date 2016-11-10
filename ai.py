import copy
import random
from random import shuffle
import go
import randomai

class AI:
    player = ''
    otherPlayer = ''
    boardsize = 9

    def __init__(self, player, boardsize):
        self.player = player
        self.otherPlayer = 'o' if player == 'x' else 'x'
        self.boardsize = boardsize

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

        for x in range(len(gamestate)):
            for y in range(len(gamestate[x])):
                if gamestate[x][y] == '-':
                    available.append([x, y])

        return available

    def place(self, gamestate, x, y):
        gamestate[x][y] = self.player



    def turn(self, gamestate):
        available = self.availableMoves(gamestate)


        rank = []
        for move in range(len(available)):
            rank.append([available[move], 0])

            for i in range(5):
                ai1 = randomai.RandomAI('x', self.boardsize)
                ai2 = randomai.RandomAI('o', self.boardsize)

                newstate = copy.deepcopy(gamestate)
                self.place(newstate, available[move][0], available[move][1])

                res = go.begin(lambda state: ai1.turn(state), lambda state: ai2.turn(state), newstate, self.otherPlayer, False, self.boardsize)

                if res == self.player:
                    rank[move][1]+=1
                elif res != 'tie':
                    rank[move][1]-=1

        bestmove = max(rank, key=lambda x: x[1])
        print(bestmove)
        return bestmove[0]