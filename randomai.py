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

    def turn(self, gamestate):

        x = random.randint(0, self.boardsize - 1)
        y = random.randint(0, self.boardsize - 1)

        if gamestate[x][y] == "-":
            me, enemy = self.score(gamestate)
            if me + 12 < enemy:
                print("forfeit")
                return "forfeit"

            return [y, x]
        else:
            return self.turn(gamestate)