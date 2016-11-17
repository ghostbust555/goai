from __future__ import print_function

import theano
from keras.engine import Input
from keras.engine import Merge
from keras.engine import Model
from keras.engine import merge

import go

import re
from random import shuffle

import numpy as np
np.random.seed(1337)  # for reproducibility

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, advanced_activations
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
    nb_epoch = 120
    rows, cols = boardSize, boardSize
    # number of convolutional filters to use
    nb_1_filters = 32
    nb_2_filters = 16
    # size of pooling area for max pooling
    pool_size = (3, 3)
    # convolution kernel size
    kernel_1_size = (5, 5)
    kernel_2_size = (3, 3)

    totalInputs = []
    totalOutputs = []

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
    inputStates = []
    outputStates = []

    def alphaToXY(self, alpha):
        x = ord(alpha[0]) - 97
        y = ord(alpha[1]) - 97

        return x, y

    def getIntRep(self, val, xoro):
        if val == '-':
            return 0
        elif val == xoro:
            return 1
        else:
            return -1

    def convertBoardStateToTensor(self, state, xoro):
        return [[self.getIntRep(y, xoro) for y in x] for x in state]

    def aiStep(self, savedGame, state):
        if self.index >= len(savedGame.moves):
            return "forfeit"

        move = savedGame.moves[self.index]
        empty = np.zeros((self.boardSize, self.boardSize))

        black = move[0] == "B"
        moveVal = move[1]

        cbs = self.convertBoardStateToTensor(state, 'x' if black else 'o')
        self.inputStates.append([cbs])

        self.index += 1

        if moveVal == "":
            self.outputStates.append([empty])
            return "pass"

        x, y = self.alphaToXY(moveVal)
        empty[x][y] = 1
        self.outputStates.append([empty])

        return x, y

    def getGameAsBoardStates(self, savedGame):
        game = go.Go()

        self.index = 0

        game.begin(lambda state: self.aiStep(savedGame, state),
                 lambda state: self.aiStep(savedGame, state))

    def inceptionFunctional(self, input):
        input_img = input

        t1 = Convolution2D(64, 1, 1, border_mode='same', activation='relu')(input_img)
        tower_1 = Convolution2D(64, 3, 3, border_mode='same', activation='relu')(t1)

        t2 = Convolution2D(64, 1, 1, border_mode='same', activation='relu')(input_img)
        tower_2 = Convolution2D(64, 5, 5, border_mode='same', activation='relu')(t2)

        t3 = MaxPooling2D((3, 3), strides=(1, 1), border_mode='same')(input_img)
        tower_3 = Convolution2D(64, 1, 1, border_mode='same', activation='relu')(t3)

        return merge([tower_1, tower_2, tower_3], mode='concat', concat_axis=1)

    def inceptionLayer(self, input_shape):

        branch_one = Sequential()
        branch_one.add(Convolution2D(8, 1, 1,
                                      border_mode='same',
                                      input_shape=input_shape))

        branch_two = Sequential()
        branch_one.add(Convolution2D(32, 1, 1,
                                     border_mode='same',
                                     input_shape=input_shape))
        branch_two.add(Convolution2D(32, 3, 3,
                                border_mode='same',
                                input_shape=input_shape))

        branch_three = Sequential()
        branch_one.add(Convolution2D(32, 1, 1,
                                 border_mode='same',
                                 input_shape=input_shape))
        branch_three.add(Convolution2D(32, 3, 3,
                                border_mode='same',
                                input_shape=input_shape))
        branch_three.add(Convolution2D(32, 3, 3,
                                border_mode='same',
                                input_shape=input_shape))

        merged = Merge([branch_one, branch_two, branch_three], mode='concat', concat_axis=1)
        return merged

    def makeModelFunctional(self, input):
        x1 = self.inceptionFunctional(input)

        x2 = Convolution2D(self.nb_2_filters, self.kernel_2_size[0], self.kernel_2_size[1], activation='relu')(x1)
        x3 = MaxPooling2D(pool_size=self.pool_size)(x2)
        x4 = Dropout(.1)(x3)
        x5 = Flatten()(x4)
        x6 = Dense(512, activation='relu')(x5)
        x7 = Dense(self.nb_output, activation='softmax')(x6)

        self.model = Model(input=input, output=x1)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer='adadelta',
                           metrics=['accuracy'])

    def makeModel(self):
        self.model = Sequential()

        input_shape = (1, self.rows, self.cols)

        merged1 = self.inceptionLayer(input_shape)

        self.model.add(merged1)
        self.model.add(Convolution2D(self.nb_2_filters, self.kernel_2_size[0], self.kernel_2_size[1]))
        self.model.add(advanced_activations.SReLU())
        self.model.add(MaxPooling2D(pool_size=self.pool_size))
        self.model.add(Dropout(0.1))

        self.model.add(Flatten())
        self.model.add(Dense(512))
        self.model.add(advanced_activations.ELU())
        self.model.add(Dense(256))
        self.model.add(advanced_activations.ELU())
        self.model.add(Dropout(0.1))
        self.model.add(Dense(self.nb_output))
        self.model.add(Activation('softmax'))

        self.model.compile(loss='categorical_crossentropy',
                      optimizer='adadelta',
                      metrics=['accuracy'])

    def getModelDataFormat(self, inputStates, outputStates):
        take = int(len(inputStates)*.8)

        x_train = inputStates[:take].astype('float32')
        x_test = inputStates[take:].astype('float32')
        y_train = (outputStates[:take]).reshape(take, self.boardSize*self.boardSize)
        y_test = (outputStates[take:]).reshape(len(outputStates) - take, self.boardSize*self.boardSize)

        print('X_train shape:', x_train.shape)
        print(x_train.shape[0], 'train samples')
        print(x_test.shape[0], 'test samples')

        return x_train, x_test, y_train, y_test

    def trainOnGames(self, savedGames):
        for savedGame in savedGames[:10000]:
            self.getGameAsBoardStates(savedGame)

        x_train, x_test, y_train, y_test = self.getModelDataFormat(np.array(self.inputStates), np.array(self.outputStates))

        input_shape = (1, self.rows, self.cols)
        input = Input(shape=input_shape)

        self.makeModelFunctional(input)

        self.model.fit(x_train, y_train, batch_size=self.batch_size, nb_epoch=self.nb_epoch, verbose=1, validation_data=(x_test, y_test))
        score = self.model.evaluate(x_test, y_test, verbose=0)
        print('Test score:', score[0])
        print('Test accuracy:', score[1])

        self.model.save_weights("savedNetwork")

        pass

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

theano.config.blas.ldflags = "-LC:/Users/kyle.flanigan/PycharmProjects/foriertest/mkl -lmkl_core -lmkl_intel_thread -lmkl_lapack95_lp64 -lmkl_blas95_lp64 -lmkl_rt"
print('blas.ldflags=', theano.config.blas.ldflags)
tnt = TestNeuralTrainer()
#tnt.makeModelFunctional()
tnt.loadFile()