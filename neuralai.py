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

savednetwork = "savedNetwork-inceptionnet"

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
        with open(savednetwork+'.json') as jsonfile:
            data = jsonfile.read().replace('\n', '')
        self.model = keras.models.model_from_json(data)
        self.model.load_weights(savednetwork+".h5")

        dir_path = os.path.dirname(os.path.realpath(__file__))+"\\openblas"
        if os.name == "nt":
            os.environ["PATH"] += os.pathsep + dir_path
            theano.config.blas.ldflags = "-L"+dir_path+" -lopenblas"
            print('blas.ldflags=', theano.config.blas.ldflags)

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