from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait, as_completed
from queue import Queue

import copy
import random

from random import shuffle

import sys

import aiutils
import randomai
import go

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

TRIES_PER_STATE = 5
MAX_WORKERS = 7

USE_MUTITHREAD = True


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


    def turnSingleThread(self, gamestate, game):
        available = self.availableMoves(gamestate)

        rank = []
        for move in available:
            res = aiutils.montecarlo(move, self.boardsize, gamestate, self.player, self.otherPlayer, TRIES_PER_STATE)
            rank.append(res)

        rank = filter(lambda x: x[1] is not None, rank)
        bestmoves = sorted(rank, key=lambda x: x[1], reverse=True)

        for move in bestmoves:
            newstate = go.Go.copyState(gamestate)


            if aiutils.place(self.player, newstate, move[0][0], move[0][1]) and game.testgoodmove(newstate):
                print(move)
                return [move[0][0], move[0][1]]

        return 'forfeit'

    def turn(self, gamestate, game):
        if USE_MUTITHREAD:
            futures = []
            available = self.availableMoves(gamestate)

            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
                for move in available:
                    futures.append(executor.submit(aiutils.montecarlo, move, self.boardsize, gamestate, self.player, self.otherPlayer, TRIES_PER_STATE))

            results = list(wait(futures).done)

            rank = [o._result for o in results]
            rank = filter(lambda x: x[1] is not None, rank)
            rank = filter(lambda x: x[1] is not None, rank)

            bestmoves = sorted(rank, key=lambda x: x[1], reverse=True)

            for move in bestmoves:
                newstate = go.Go.copyState(gamestate)
                aiutils.place(self.player, newstate, move[0][0], move[0][1])

                if game.testgoodmove(newstate):
                    print(move)
                    return [move[0][0], move[0][1]]

            return 'forfeit'

        else:
            return self.turnSingleThread(gamestate, game)