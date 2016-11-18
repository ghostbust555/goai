import numpy as np

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

def tensorToMoves(state):
    return np.array(state).argsort(axis=None)[::-1]