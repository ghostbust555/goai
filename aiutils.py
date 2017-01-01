import math
import numpy as np

import go
import randomai


def alphaToXY(alpha):
    x = ord(alpha[0]) - 97
    y = ord(alpha[1]) - 97

    return x, y

def getIntRep(val, xoro):
    if val == '-':
        return 0
    elif val == xoro:
        return 1
    else:
        return -1

def convertBoardStateToTensor(state, xoro):
    return [[getIntRep(y, xoro) for y in x] for x in state]

def vectorToMoves(state):
    boardsize = math.sqrt(len(state[0]))
    bestMoveIndexes = sorted(range(len(state[0])), key=lambda k: state[0][k], reverse=True)

    bestMoveLocations = []
    for index in bestMoveIndexes:
        bestMoveLocations.append([math.floor(index / boardsize), math.floor(index % boardsize), state[0][index]])

    return bestMoveLocations

def vectorToMoves2D(state):
    state = (state[0][0])
    state = np.array(state).flatten()
    state=state.tolist()
    return vectorToMoves([state])


def montecarlo(currentMove, boardsize, gamestate, player, otherPlayer, TRIES_PER_STATE):
    score = 0
    for i in range(TRIES_PER_STATE):
        ai1 = randomai.RandomAI('x', boardsize)
        ai2 = randomai.RandomAI('o', boardsize)

        newstate = go.Go.copyState(gamestate)
        if place(player, newstate, currentMove[0], currentMove[1]):

            game = go.Go()
            res = game.begin(lambda state: ai1.turn(state, game), lambda state: ai2.turn(state, game), newstate, otherPlayer, False, boardsize)

            if res == player:
                score += 1
            elif res != 'tie':
                score -= 1
        else:
            return [currentMove, -1000]

    return [currentMove, score]


def place(player, gamestate, x, y):
    if gamestate[x][y] == '-':
        gamestate[x][y] = player
        return True
    else:
        return False