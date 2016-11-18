import ai
import randomai
from go import Go

boardsize = 9

def main():
    randomAi = randomai.RandomAI('x', boardsize)
    neuralAi = neuralai.NeuralAI('x', boardsize)
    ai2 = ai.AI('o', boardsize)

    game = Go()
    game.begin(lambda state: neuralAi.turn(state, game), lambda state: ai2.turn(state, game), None, 'x', True, boardsize)

if __name__ == '__main__':
    import neuralai
    main()
