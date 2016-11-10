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

        x = random.randint(0, self.boardsize - 1)
        y = random.randint(0, self.boardsize - 1)

        if gamestate[x][y] == "-":
            newstate = copy.deepcopy(gamestate)
            self.place(newstate, x, y)

            if game.testgoodmove(newstate):

                me, enemy = self.score(gamestate)
                if me + 12 < enemy:
                    #print("forfeit")
                    return "forfeit"

                return [y, x]
            else:
                return self.turn(gamestate, game)
        else:
            return self.turn(gamestate, game)