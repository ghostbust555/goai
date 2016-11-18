import numpy as np
import math

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
