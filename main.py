import ai
import randomai
import neuralai
from go import Go

boardsize = 9

def main():
    ai1 = neuralai.NeuralAI('x', boardsize)
    ai2 = ai.AI('o', boardsize)

    game = Go()
    game.begin(lambda state: ai1.turn(state, game), lambda state: ai2.turn(state, game), None, 'x', True, boardsize)

if __name__ == '__main__':
    main()
