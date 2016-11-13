from __future__ import print_function

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
    batch_size = 128
    nb_output = 9 * 9
    nb_epoch = 12
    img_rows, img_cols = 9, 9
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

    def makeModel(self):
        self.model = Sequential()

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

    def trainOnGames(self, savedGames):


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

TestNeuralTrainer().loadFile()