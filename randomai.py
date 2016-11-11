import copy
import random

class RandomAI:
    boardsize = 9
    player = ''

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

    def turn(self, gamestate, game):
        available = self.availableMoves(gamestate)
        random.shuffle(available)

        for move in available:
            newstate = copy.deepcopy(gamestate)
            self.place(newstate, move[0], move[1])

            if game.testgoodmove(newstate):
                return [move[1], move[0]]

        return 'forfeit'