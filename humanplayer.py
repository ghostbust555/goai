import copy
import random

import time

import go

class HumanPlayer:
    boardsize = 9
    player = ''
    move = []

    def __init__(self, player, boardsize):
        self.player = player
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

    def makeMove(self, x, y):
        self.move = [x, y]

    def turn(self, gamestate, game):
        while True:
            if self.move:
                m = self.move
                self.move = []
                return m
            time.sleep(.5)

        return "pass"
