import go
import ai
import randomai

boardsize = 5

ai1 = randomai.RandomAI('x', boardsize)
ai2 = randomai.RandomAI('o', boardsize)

game = go.Go()
game.begin(lambda state: ai1.turn(state), lambda state: ai2.turn(state), None, 'x', True, boardsize)
