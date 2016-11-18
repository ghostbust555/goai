from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait, as_completed
from queue import Queue

import copy
import json
import random

from random import shuffle

import keras

import numpy as np

import os

import sys

import theano

import go
import randomai
from ai import AI
from go import Go

import aiutils

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

TRIES_PER_STATE = 5
MAX_WORKERS = 7

USE_MUTITHREAD = True


class NeuralAI:
    player = ''
    otherPlayer = ''
    boardsize = 9
    model = None

    def __init__(self, player, boardsize):
        self.player = player
        self.otherPlayer = 'o' if player == 'x' else 'x'
        self.boardsize = boardsize

        data = ""
        with open('savedNetwork.json') as jsonfile:
            data = jsonfile.read().replace('\n', '')
        self.model = keras.models.model_from_json(data)
        self.model.load_weights("savedNetwork.h5")

        dir_path = os.path.dirname(os.path.realpath(__file__))
        theano.config.blas.ldflags = "-L" + dir_path + "/mkl -lmkl_core -lmkl_intel_thread -lmkl_lapack95_lp64 -lmkl_blas95_lp64 -lmkl_rt"

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
        if gamestate[x][y] == '-':
            gamestate[x][y] = player
            return True
        else:
            return False

    # @staticmethod
    # def montecarlo(currentMove, boardsize, gamestate, player, otherPlayer):
    #     score = 0
    #     for i in range(TRIES_PER_STATE):
    #         ai1 = randomai.RandomAI('x', boardsize)
    #         ai2 = randomai.RandomAI('o', boardsize)
    #
    #         newstate = Go.copyState(gamestate)
    #         AI.place(player, newstate, currentMove[0], currentMove[1])
    #
    #         game = Go()
    #         res = game.begin(lambda state: ai1.turn(state, game), lambda state: ai2.turn(state, game), newstate, otherPlayer, False, boardsize)
    #
    #         if res == player:
    #             score += 1
    #         elif res != 'tie':
    #             score -= 1
    #
    #     return [currentMove, score]

    # def turnSingleThread(self, gamestate, game):
    #     available = self.availableMoves(gamestate)
    #
    #     rank = []
    #     for moveIdx in range(len(available)):
    #         move = available[moveIdx]
    #         res = AI.montecarlo(move, self.boardsize, gamestate, self.player, self.otherPlayer)
    #         rank.append(res)
    #
    #     rank = filter(lambda x: x[1] is not None, rank)
    #     bestmoves = sorted(rank, key=lambda x: x[1], reverse=True)
    #
    #     for move in bestmoves:
    #         newstate = Go.copyState(gamestate)
    #         self.place(self.player, newstate, move[0][0], move[0][1])
    #
    #         if game.testgoodmove(newstate):
    #             print(move)
    #             return [move[0][1], move[0][0]]
    #
    #     return 'forfeit'

    def turn(self, gamestate, game):
        i = aiutils.convertBoardStateToTensor(gamestate, self.player)
        res = self.model.predict(np.array([[i]]))

        bestmoves = aiutils.vectorToMoves(res)

        for move in bestmoves:
            newstate = Go.copyState(gamestate)

            if NeuralAI.place(self.player, newstate, move[0], move[1]) and game.testgoodmove(newstate):
                print(move)
                return [move[0], move[1]]

        print('forfeit')
        print(bestmoves)
        return 'forfeit'

        # if USE_MUTITHREAD:
        #     futures = []
        #     available = self.availableMoves(gamestate)
        #
        #     with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        #         #rank = []
        #         for moveIdx in range(len(available)):
        #             move = available[moveIdx]
        #
        #             futures.append(executor.submit(AI.montecarlo, move, self.boardsize, gamestate, self.player, self.otherPlayer))
        #
        #     results = list(wait(futures).done)
        #
        #     rank = [o._result for o in results]
        #     rank = filter(lambda x: x[1] is not None, rank)
        #     rank = filter(lambda x: x[1] is not None, rank)
        #
        #     bestmoves = sorted(rank, key=lambda x: x[1], reverse=True)
        #
        #     for move in bestmoves:
        #         newstate = Go.copyState(gamestate)
        #         self.place(self.player, newstate, move[0][0], move[0][1])
        #
        #         if game.testgoodmove(newstate):
        #             print(move)
        #             return [move[0][1], move[0][0]]
        #
        #     return 'forfeit'
        #
        # else:
        #     return self.turnSingleThread(gamestate, game)