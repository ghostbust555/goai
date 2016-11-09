import random

class RandomAI:

    def __init__(self):
        pass

    def turn(self, gamestate):

        x = random.randint(0, 8)
        y = random.randint(0, 8)

        if gamestate[x][y] == "-":
            return [y, x]
        else:
            return self.turn(gamestate)