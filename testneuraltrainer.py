from __future__ import print_function

from go import Go

import re
from random import shuffle

import numpy as np
np.random.seed(1337)  # for reproducibility

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.utils import np_utils
from keras import backend as K


class SavedGame:
    winner = ""
    size = 0
    moves = []

class TestNeuralTrainer:
    boardSize = 9

    batch_size = 128
    nb_output = boardSize*boardSize
    nb_epoch = 12
    rows, cols = boardSize, boardSize
    # number of convolutional filters to use
    nb_filters = 16
    # size of pooling area for max pooling
    pool_size = (3, 3)
    # convolution kernel size
    kernel_size = (3, 3)

    model = None

    def loadFile(self):
        savedGames = []

        with open("combined9x9.sgf", encoding='utf16') as file:

            game = ""

            for line in file:
                if line.startswith("(;"):
                    game = line

                elif line.startswith("----------"):
                    savedGames.append(self.processGame(game))
                else:
                    game += line

        shuffle(savedGames)
        self.trainOnGames(savedGames)

    index = 0
    wInputStates = []
    wOutputStates = []

    bInputStates = []
    bOutputStates = []

    def place(self, gamestate, x, y):
        gamestate[x][y] = self.player

    def alphaToXY(self, alpha):
        x = ord(alpha[0]) - 97
        y = ord(alpha[1]) - 97

        return x, y

    def aiStep(self, savedGame,state):
        move = savedGame.moves[self.index]
        empty = np.zeros(self.boardSize, self.boardSize)
        if move[1] == "":
            self.index+=1
            if move[0] == "B":
                self.bOutputStates.append(empty)
            else:
                self.wOutputStates.append(empty)
            return "pass"

        self.index+=1

        x, y = self.alphaToXY(move[1])
        empty[x][y] = 1
        if move[0] == "B":
            self.bOutputStates.append(empty)
        else:
            self.wOutputStates.append(empty)

        return x, y

    def getGameAsBoardStates(self, savedGame):
        go = Go()

        self.index = 0

        go.begin(lambda state: self.aiStep(savedGame, state),
                 lambda state: self.aiStep(savedGame, state))

    def makeModel(self):
        self.model = Sequential()

        input_shape = (1, self.rows, self.cols)

        self.model.add(Convolution2D(self.nb_filters, self.kernel_size[0], self.kernel_size[1],
                                border_mode='valid',
                                input_shape=input_shape))
        self.model.add(Activation('relu'))
        self.model.add(Convolution2D(self.nb_filters, self.kernel_size[0], self.kernel_size[1]))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=self.pool_size))
        self.model.add(Dropout(0.25))

        self.model.add(Flatten())
        self.model.add(Dense(128))
        self.model.add(Activation('relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(self.nb_output))
        self.model.add(Activation('softmax'))

        self.model.compile(loss='categorical_crossentropy',
                      optimizer='adadelta',
                      metrics=['accuracy'])

    def getModelDataFormat(self, savedGames):
        (X_train, y_train), (X_test, y_test) = savedGames

        X_train = X_train.reshape(X_train.shape[0], 1, self.rows, self.cols)
        X_test = X_test.reshape(X_test.shape[0], 1, self.rows, self.cols)


        X_train = X_train.astype('float32')
        X_test = X_test.astype('float32')
        X_train /= 255
        X_test /= 255
        print('X_train shape:', X_train.shape)
        print(X_train.shape[0], 'train samples')
        print(X_test.shape[0], 'test samples')

        # convert class vectors to binary class matrices
        Y_train = np_utils.to_categorical(y_train, self.nb_output)
        Y_test = np_utils.to_categorical(y_test, self.nb_output)

    def trainOnGames(self, savedGames):
        self.getModelDataFormat(savedGames)

    def processGame(self, gameString:str):
        winner = ""
        size = 0
        moves = []

        matches = re.findall(r'(?:\(;)*(.{2})\[(.*)\]', gameString)

        for match in matches:
            code = match[0]
            value = match[1]

            if code == "RE":
                winner = value[0]
            elif code == "SZ":
                size = int(value)
            elif code == ";B":
                moves.append(["B", value])
            elif code == ";W":
                moves.append(["W", value])

        sg = SavedGame()
        sg.winner = winner
        sg.size = size
        sg.moves = moves

        return sg

tnt = TestNeuralTrainer()
tnt.makeModel()
tnt.loadFile()