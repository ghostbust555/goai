import ai
import randomai
import neuralai
from go import Go

boardsize = 11

def main():
    ai1 = ai.AI('x', boardsize)
    ai2 = neuralai.NeuralAI('o', boardsize)

    game = Go()
    game.begin(lambda state: ai1.turn(state, game), lambda state: ai2.turn(state, game), None, 'x', True, boardsize)

if __name__ == '__main__':
    main()
