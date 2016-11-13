import ai
import randomai
from go import Go

boardsize = 11

def main():
    ai1 = ai.AI('x', boardsize)
    ai2 = randomai.RandomAI('o', boardsize)

    game = Go()
    game.begin(lambda state: ai1.turn(state, game), lambda state: ai2.turn(state, game), None, 'x', True, boardsize)

if __name__ == '__main__':
    main()
