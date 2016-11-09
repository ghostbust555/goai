import go
import ai
import randomai

ai1 = ai.AI('x')
ai2 = randomai.RandomAI()

go.begin(lambda state: ai1.turn(state), lambda state: ai2.turn(state))
