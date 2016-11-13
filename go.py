import copy
import time

import ai
import randomai


class Go:
    boardsize = 5
    o_groups = []
    x_groups = []

    o_points = []
    x_points = []

    def initalize(self):
        gs = []
        for i in range(0, self.boardsize):
            gs.append([])
            for j in range(0, self.boardsize):
                gs[i].append('-')
        return gs


    ## Provides an ascii display of the Go board
    def printboard(self, gs):
        for row in gs:
            rowprint = ''
            for element in row:
                rowprint += element
                rowprint += ' '
            print(rowprint)

            ## Returns a string that describes the game state

    @staticmethod
    def readable(gs):
        readthis = ''
        readthis += '<<'
        for row in gs:
            for element in row:
                readthis += element
        readthis += '>>'
        return readthis

    def addpoint(self, x, y, xoro):
        self.gsf[x][y] = xoro

    @staticmethod
    def getAdjacentDiagonal(x, y, boardsize):
        result = []

        oneLessBoardsize = boardsize - 1
        oneLessX = x-1
        oneLessY = y-1
        oneMoreX = x+1
        oneMoreY = y+1

        if x > 0 and y > 0:
            result.append([oneLessX,oneLessY])

        if x > 0 and y < oneLessBoardsize:
            result.append([oneLessX, oneMoreY])

        if x < boardsize - 1 and y < oneLessBoardsize:
            result.append([oneMoreX, oneMoreY])

        if x < oneLessBoardsize and y > 0:
            result.append([oneMoreX, oneLessY])

        return result

    @staticmethod
    def getAdjacentCardinal(x, y, boardsize):
        result = []

        oneLessBoardsize = boardsize - 1

        if x > 0:
            result.append([x-1,y])

        if y > 0:
            result.append([x, y-1])

        if x < oneLessBoardsize:
            result.append([x + 1, y])

        if y < oneLessBoardsize:
            result.append([x, y + 1])

        return result


    def findMyGroup(self,x,y,state):
        visited, queue = set(), [[x, y]]
        captured = True

        xoro = state[x][y]

        while queue:
            vertex = tuple(queue.pop(0))
            x = vertex[0]
            y = vertex[1]
            if state[x][y] == xoro and vertex not in visited:
                visited.add(vertex)
                cardinal = Go.getAdjacentCardinal(x, y, self.boardsize)
                queue.extend(cardinal)

                if captured:
                    for car in cardinal:
                        if state[car[0]][car[1]] == '-':
                            captured = False
                            break

                queue.extend(Go.getAdjacentDiagonal(x, y, self.boardsize))

        return visited, captured

    def removeGroup(self,group,state):
        for m in group:
            state[m[0]][m[1]] = '-'

    def groupPiecesAndCapture(self, state):
        seenBoard = self.initalize()

        self.x_groups = []
        self.o_groups = []

        for x in range(len(state)):
            for y in range(len(state[x])):
                if seenBoard[x][y] == '-' and state[x][y] != '-':
                    group, captured = self.findMyGroup(x, y, state)
                    if captured:
                        self.removeGroup(group,state)
                    elif state[x][y] == 'x':
                        self.x_groups.append(group)
                    elif state[x][y] == 'o':
                        self.o_groups.append(group)

                    for m in group:
                        seenBoard[m[0]][m[1]] = "+"

        return self.x_groups, self.o_groups

    def testgoodmove(self, state):
        if self.readable(state) not in self.gscache:
            return True
        else:
            return False

    def getScores(self, state, xoro):
        myscore = 0
        enemyscore = 0

        for x in range(len(state)):
            for y in range(len(state[x])):
                if state[x][y] == xoro:
                    myscore += 1
                elif state[x][y] != '-':
                    enemyscore += 1

        return myscore, enemyscore

    @staticmethod
    def copyState(state):
        copy = [x[:] for x in state]
        return copy

    def turn(self, playerTurn, showOutput=False):
        self.gsf = Go.copyState(self.gsc)

        if showOutput:
            print()
            print('place for ' + self.xoro)

        turnResult = playerTurn(self.gsf)
        if turnResult == 'forfeit':
            self.gameover = 1
            return
        elif turnResult == 'pass':
            if self.xoro == 'o':
                self.player1_pass = True
            else:
                self.player2_pass = True

        ## If the player doesn't pass...
        else:
            self.player1_pass = False
            self.player2_pass = False

            ## The new piece is added to its group,
            ## or a new group is created for it.
            self.addpoint(turnResult[1], turnResult[0], self.xoro)
            self.groupPiecesAndCapture(self.gsf)

            ## Checks to see if the move, given all the
            ## captures it causes, would return the board
            ## to a previous game state.
            if not self.testgoodmove(self.gsf):
                if showOutput:
                    print('invalid move - that returns to board to a previous state')


                self.turn(playerTurn,showOutput)
            else:
                self.gsc = self.gsf
                self.gscache += self.readable(self.gsf)

        if (self.player1_pass == 1) & (self.player2_pass == 1):
            self.gameover = 1
            return

        myscore, enemyscore = self.getScores(self.gsc, self.xoro)

        if self.xoro == 'o':
            self.o_points = myscore
            self.x_points = enemyscore
        else:
            self.x_points = myscore
            self.o_points = enemyscore

        if myscore + 10 < enemyscore:
            self.gameover = 1

    def begin(self, player1turn, player2turn, initialState=None, startingPlayer='x', showOutput = False, board_size=9):
        self.boardsize = board_size

        ## Creates a blank game state - a blank board
        self.gsc = self.initalize() if initialState is None else initialState
        self.gsf = Go.copyState(self.gsc)
        ## Sets initial values
        self.o_groups = []
        self.x_groups = []
        self.non_groups = []
        self.gscache = ''
        self.player1_pass = 0
        self.player2_pass = 0
        self.gameover = 0
        self.o_points = 0
        self.x_points = 0

        ## Gives players turns until the end of the game
        ## (that is, until both players pass, one after
        ## the other)
        if startingPlayer == 'o':
            while self.gameover != 1:

                ## Set it as o-player's turn
                self.xoro = 'o'
                self.notxoro = 'x'
                if showOutput:
                    print()
                    self.printboard(self.gsc)

                start = time.clock()
                self.turn(player1turn, showOutput)
                if showOutput:
                    print("{0} took {1:.2f}".format(self.xoro, time.clock() - start))

                if self.gameover == 1:
                    break

                ## Sets it as x-player's turn
                self.xoro = 'x'
                self.notxoro = 'o'
                if showOutput:
                    print()
                    self.printboard(self.gsc)

                start = time.clock()
                self.turn(player2turn, showOutput)
                if showOutput:
                    print("{0} took {1:.2f}".format(self.xoro, time.clock() - start))
        else:
            while self.gameover != 1:

                ## Set it as o-player's turn
                self.xoro = 'x'
                self.notxoro = 'o'
                if showOutput:
                    print()
                    self.printboard(self.gsc)

                start = time.clock()
                self.turn(player1turn, showOutput)
                if showOutput:
                    print("{0} took {1:.2f}".format(self.xoro, time.clock() - start))

                if self.gameover == 1:
                    break

                ## Sets it as x-player's turn
                self.xoro = 'o'
                self.notxoro = 'x'
                if showOutput:
                    print()
                    self.printboard(self.gsc)

                start = time.clock()
                self.turn(player2turn, showOutput)
                if showOutput:
                    print("{0} took {1:.2f}".format(self.xoro, time.clock() - start))

        if showOutput:
            print()
            print('final board:')
            print()
            self.printboard(self.gsc)
            print()
            print('o points: ', str(self.o_points))
            print('x points: ', str(self.x_points))
        ## Determines the winner
        if self.o_points > self.x_points:
            if showOutput:
                print('o wins')

            return 'o'

        elif self.x_points > self.o_points:
            if showOutput:
                print('x wins')
            return 'x'
        else:
            if showOutput:
                print('tie')
            return 'tie'


# boardsize = 5
# ai1 = ai.AI('x', boardsize)
# ai2 = randomai.RandomAI('o', boardsize)
#
# game = GoTest()
#
# initstate = [['o','-','-','o','o'],
#              ['o','-','-','o','x'],
#              ['o','-','-','o','x'],
#              ['o','-','-','o','x'],
#              ['-','-','-','o','o']]
# game.printboard(initstate)
# #game.groupPiecesAndCapture(initstate)
#
#
# game.begin(lambda state: ai1.turn(state, game), lambda state: ai2.turn(state, game), None, 'x', True, boardsize)