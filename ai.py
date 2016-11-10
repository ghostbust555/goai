import copy
import random
from concurrent.futures import ProcessPoolExecutor, wait, as_completed
from queue import Queue
from random import shuffle

import sys

import go
import randomai


CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

TRIES_PER_STATE = 3
MAX_WORKERS = 7

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

    @staticmethod
    def place(player, gamestate, x, y):
        gamestate[x][y] = player

    @staticmethod
    def montecarlo(currentMove, boardsize, gamestate, player, otherPlayer):
        score = 0
        for i in range(TRIES_PER_STATE):
            ai1 = randomai.RandomAI('x', boardsize)
            ai2 = randomai.RandomAI('o', boardsize)

            newstate = copy.deepcopy(gamestate)
            AI.place(player, newstate, currentMove[0], currentMove[1])

            game = go.Go()
            res = game.begin(lambda state: ai1.turn(state, game), lambda state: ai2.turn(state, game), newstate, otherPlayer, False, boardsize)

            if res == player:
                score += 1
            elif res != 'tie':
                score -= 1

        return [currentMove, score]

    def turn(self, gamestate, game):
        futures = []
        available = self.availableMoves(gamestate)

        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            #rank = []
            for moveIdx in range(len(available)):
                move = available[moveIdx]

                futures.append(executor.submit(AI.montecarlo, move, self.boardsize, gamestate, self.player, self.otherPlayer))

                #print("Trying move ",moveIdx," of ",len(available))
                #score = AI.montecarlo(move, self.boardsize, gamestate, self.player, self.otherPlayer, q)

        results = list(wait(futures).done)

        rank = [o._result for o in results]

        bestmoves = sorted(rank, key=lambda x: x[1], reverse=True)

        for move in bestmoves:
            newstate = copy.deepcopy(gamestate)
            self.place(self.player, newstate, move[0][0], move[0][1])

            if game.testgoodmove(newstate):
                print(move)
                return [move[0][1], move[0][0]]

        print("BLOWING IT. Default to random")
        return randomai.RandomAI(self.otherPlayer, self.boardsize).turn(gamestate)