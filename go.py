import copy
import time

class Go:

    boardsize = 5
    gameon = 1
    restore_o = []
    restore_x = []
    xoro = 'x'
    notxoro = 'o'
    player1_pass = 0
    player2_pass = 0
    gameover = 0
    gsf = []
    gsc = []
    gsp = []
    o_groups = []
    x_groups = []
    non_groups = []
    gscache = []
    o_points = 0
    x_points = 0
    edited = False


    ## Generates blank game states
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


    ## Returns a list of the board positions surrounding the
    ## passed group.
    def gperm(self, group):
        permimeter = []
        hit = 0
        loss = 0
        ## Adds permimeter spots below
        ## Works by looking from top to bottom, left to right,
        ## at each posisition on the board.  When a posistion
        ## is hit that is in the given group, I set hit = 1.
        ## Then, at the next position that is not in that group,
        ## or if the end of the column is reached, I set loss = 1.
        ## That point is the first point below a point in that group,
        ## so it is part of the permieter of that group.
        i = 0
        j = 0
        while i < self.boardsize:
            j = 0
            hit = 0
            while j < self.boardsize:
                if [i, j] in group:
                    hit = 1
                elif (hit == 1) & ([i, j] not in group):
                    loss = 1
                if (hit == 1) & (loss == 1):
                    permimeter.append([i, j])
                    hit = 0
                    loss = 0
                j += 1
            i += 1
        ## Adds permimeter spots to the right
        i = 0
        j = 0
        while i < self.boardsize:
            j = 0
            hit = 0
            while j < self.boardsize:
                if [j, i] in group:
                    hit = 1
                elif (hit == 1) & ([j, i] not in group):
                    loss = 1
                if (hit == 1) & (loss == 1):
                    permimeter.append([j, i])
                    hit = 0
                    loss = 0
                j += 1
            i += 1
        ## Adds permimeter spots above
        i = 0
        j = self.boardsize - 1
        while i < self.boardsize:
            j = self.boardsize - 1
            hit = 0
            while j >= 0:
                if [i, j] in group:
                    hit = 1
                elif (hit == 1) & ([i, j] not in group):
                    loss = 1
                if (hit == 1) & (loss == 1):
                    permimeter.append([i, j])
                    hit = 0
                    loss = 0
                j -= 1
            i += 1
        ## Adds permimeter spots to the left
        i = 0
        j = self.boardsize - 1
        while i < self.boardsize:
            j = self.boardsize - 1
            hit = 0
            while j >= 0:
                if [j, i] in group:
                    hit = 1
                elif (hit == 1) & ([j, i] not in group):
                    loss = 1
                if (hit == 1) & (loss == 1):
                    permimeter.append([j, i])
                    hit = 0
                    loss = 0
                j -= 1
            i += 1
        return permimeter


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


    ## Counts the territory captured by each player
    def count(self):
        ## Creates a list of groups (non_groups) of empty positions.
        for i in range(0, self.boardsize):
            for j in range(0, self.boardsize):
                if self.gsc[j][i] == '-':
                    new = 1
                    for group in self.non_groups:
                        if [i, j] in self.gperm(group):
                            group.append([i, j])
                            new = 0
                    if new == 1:
                        self.non_groups.append([[i, j]])
        self.concat('-')

        self.o_points = 0
        self.x_points = 0

        ## Gives a point to the each player for every pebble they have
        ## on the board.
        for group in self.o_groups:
            self.o_points += len(group)
        for group in self.x_groups:
            self.x_points += len(group)

        ## The permimeter of these empty positions is here considered,
        ## and if every position in the permimeter of a non_group is
        ## one player or the other, that player gains a number of points
        ## equal to the length of that group (the number of positions
        ## that their pieces enclose).
        for group in self.non_groups:
            no = 0
            for element in self.gperm(group):
                if self.gsc[element[1]][element[0]] != 'o':
                    no = 1
            if no == 0:
                self.o_points += len(group)

        for group in self.non_groups:
            no = 0
            for element in self.gperm(group):
                if self.gsc[element[1]][element[0]] != 'x':
                    no = 1
            if no == 0:
                self.x_points += len(group)


    ## Checks for capture, and removes the captured pieces from the board
    def capture(self,xoro):
        if xoro == 'o':
            groups = self.x_groups
            otherplayer = 'o'
        else:
            groups = self.o_groups
            otherplayer = 'x'

        ## Checks to see, for each group of a particular player,
        ## whether any of the board positions in the
        ## perimeter around that group are held by the other player.
        ## If any position is not held by the other player,
        ## the group is not captured, and is safe.  Otherwise,
        ## the group is removed.  But we haven't tested this yet
        ## to see if this would return the board to a previous
        ## state, so we save the removed groups with the restore lists.
        for group in groups:
            safe = 0
            for element in self.gperm(group):
                if self.gsf[element[1]][element[0]] != otherplayer:
                    safe = 1
            if safe != 1:
                self.edited = 1
                if xoro == 'o':
                    self.restore_x.append(group)
                else:
                    self.restore_o.append(group)
                groups.remove(group)

        # Sets gsf given the new captures
        self.gsf = self.initalize()
        for group in self.o_groups:
            for point in group:
                self.gsf[point[1]][point[0]] = 'o'
        for group in self.x_groups:
            for point in group:
                self.gsf[point[1]][point[0]] = 'x'


    ## Checks to see if the new game state, created by the most recent
    ## move, returns the board to a previous state.  If not, then
    ## gsc is set as this new state, and gsp is set as what gsc was, and
    ## the new game state is stored in gscache.  The function returns 1
    ## if the move is valid, 0 otherwise.
    def goodmove(self):
        if self.readable(self.gsf) not in self.gscache:
            self.gsp = []
            self.gsc = []
            for element in self.gsf:
                self.gsp.append(element)
                self.gsc.append(element)
            self.gscache += self.readable(self.gsf)
            return 1
        else:
            return 0

    def testgoodmove(self, state):
        if self.readable(state) not in self.gscache:
            return True
        else:
            return False

    ## Checks if any groups contain the same point;
    ## if so, joins them into one group
    def concat(self,xoro):
        if xoro == 'o':
            groups = self.o_groups
        elif xoro == 'x':
            groups = self.x_groups
        else:
            groups = self.non_groups
        i = 0
        ## currentgroups and previousgroups are used to compare the number
        ## of groups before this nest of whiles to the number after.  If
        ## The number is the same, then nothing needed to be concatinated,
        ## and we can move on.  If the number is different, two groups
        ## were concatinated, and we need to run through this nest again
        ## to see if any other groups need to be joined together.
        currentgroups = len(groups)
        previousgroups = currentgroups + 1
        ## Checks if the positions contained in any group are to be
        ## found in any other group.  If so, all elements of the second are
        ## added to the first, and the first is deleted.
        while previousgroups != currentgroups:
            while i < len(groups) - 1:
                reset = 0
                j = i + 1
                while j < len(groups):
                    k = 0
                    while k < len(groups[i]):
                        if groups[i][k] in groups[j]:
                            for element in groups[j]:
                                if element not in groups[i]:
                                    groups[i].append(element)
                            groups.remove(groups[j])
                            reset = 1
                        if reset == 1:
                            break
                        k += 1
                    j += 1
                if reset == 1:
                    i = -1
                i += 1
            previousgroups = currentgroups
            currentgroups = len(groups)


    ## Adds point xy to a group if xy is in the
    ## perimeter of an existing group, or creates
    ## new group if xy is not a part of any existing group.
    def addpoint(self,xy, xoro):
        if xoro == 'o':
            groups = self.o_groups
        else:
            groups = self.x_groups
        new = 1
        for group in groups:
            if xy in self.gperm(group):
                group.append(xy)
                new = 0
        if new == 1:
            groups.append([xy])


    ## Lets the player select a move.
    def selectmove(self, xoro):
        hold = 1
        while hold == 1:

            minihold = 1
            while minihold == 1:
                pp = input('Place or pass (l/a)? ')
                if pp == 'a':
                    return 'pass'
                elif pp == 'l':
                    minihold = 0
                    ## This try...except ensures that the user
                    ## inputs only numbers
                    error = 0
                    try:
                        x = int(input('x: '))
                    except ValueError:
                        error = 1
                    try:
                        y = int(input('y: '))
                    except ValueError:
                        error = 1
                    if error == 1:
                        minihold = 1
                        print('invalid')
                else:
                    print('invalid')
            ## Ensures that the input is on the board
            if (x > self.boardsize) | (x < 0) | (y > self.boardsize) | (y < 0):
                print('invalid')
            elif self.gsc[y][x] != '-':
                print('invalid')
            else:
                hold = 0
        ## Places the piece on the 'future' board, the board
        ## used to test if a move is valid
        if xoro == 'o':
            self.gsf[y][x] = 'o'
        else:
            self.gsf[y][x] = 'x'

        return [x, y]


    ## The 'turn,' in which a player makes a move,
    ## the captures caused by that piece are made,
    ## the validity of the move is checked, and
    ## the endgame status is checked.
    def turn(self, playerTurn, showOutput=False):

        hold = 1
        while hold == 1:
            if showOutput:
                print()
                print('place for ' + self.xoro)

            turnResult = playerTurn(self.gsf)
            if turnResult == 'forfeit':
                self.gameover = 1
                return
            elif turnResult == 'pass':
                if self.xoro == 'o':
                    self.player1_pass = 1
                else:
                    self.player2_pass = 1
                hold = 0
            ## If the player doesn't pass...
            else:
                self.player1_pass = 0
                self.player2_pass = 0

                ## The new piece is added to its group,
                ## or a new group is created for it.
                self.addpoint(turnResult, self.xoro)
                ## Groups that have been connected by
                ## the this placement are joined together
                self.concat(self.xoro)
                minihold = 1
                ## Edited is a value used to check
                ## whether any capture is made.  capture()
                ## is called as many times as until no pieces
                ## are capture (until edited does not change
                ## to 1)
                edited = 0
                while minihold == 1:
                    self.restore_o = []
                    self.restore_x = []
                    self.capture(self.xoro)
                    self.capture(self.notxoro)
                    if edited == 0:
                        minihold = 0
                        edited = 0
                    else:
                        edited = 0
                ## Checks to see if the move, given all the
                ## captures it causes, would return the board
                ## to a previous game state.
                if self.goodmove() == 1:
                    hold = 0

                ## If the move is invalid, the captured groups need
                ## to be returned to the board, so we use
                ## the groups stored in the restore lists to
                ## restore the o_ and x_groups lists.
                else:
                    if showOutput:
                        print('invalid move - that returns to board to a previous state')
                    for group in self.restore_o:
                        self.o_groups.append(group)
                    for group in self.restore_x:
                        self.x_groups.append(group)
        if (self.player1_pass == 1) & (self.player2_pass == 1):
            self.gameover = 1


    ## Called to start a game
    def begin(self, player1turn, player2turn, initialState=None, startingPlayer='x', showOutput = False, board_size=9):
        self.boardsize = board_size

        ## Creates a blank game state - a blank board
        self.gsc = self.initalize() if initialState is None else initialState
        self.gsf = copy.deepcopy(self.gsc)
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

        ## Counts the score of both players
        self.count()
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
