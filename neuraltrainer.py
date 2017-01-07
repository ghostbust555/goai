from __future__ import print_function

import os
import re
from random import shuffle

#os.environ['KERAS_BACKEND'] = "theano"
#os.environ['THEANO_FLAGS'] = "device=cpu"

import numpy as np
import theano
from keras.callbacks import ModelCheckpoint
from keras.engine import Input
from keras.engine import Merge
from keras.engine import Model
from keras.engine import merge
from keras.regularizers import l2

import aiutils
import go
np.random.seed(1337)  # for reproducibility

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten, advanced_activations, UpSampling2D, Reshape, BatchNormalization, AveragePooling2D, GlobalAveragePooling2D
from keras.layers import Convolution2D, MaxPooling2D


class SavedGame:
    winner = ""
    size = 0
    moves = []

class NeuralTrainer:
    boardSize = 9

    batch_size = 150
    nb_output = boardSize*boardSize
    nb_epoch = 100
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
        count = 0
        take = 1000000

        with open("combined9x9.sgf", encoding='utf16') as file:

            game = ""

            for line in file:
                if line.startswith("(;"):
                    game = line

                elif line.startswith("----------"):
                    savedGames.append(self.processGame(game))
                    if count >= take:
                        break

                    count+=1
                else:
                    game += line
        shuffle(savedGames)
        self.trainOnGames(savedGames)

    index = 0
    inputStates = []
    outputStates = []

    def aiStep(self, savedGame, state):
        if self.index >= len(savedGame.moves):
            return "forfeit"

        move = savedGame.moves[self.index]
        empty = np.zeros((self.boardSize, self.boardSize))

        black = move[0] == "B"
        moveVal = move[1]

        cbs = aiutils.convertBoardStateToTensor(state, 'x' if black else 'o')
        self.inputStates.append([cbs])

        self.index += 1

        if moveVal == "":
            self.outputStates.append([empty])
            return "pass"

        x, y = aiutils.alphaToXY(moveVal)
        empty[x][y] = 1 if savedGame.winner == move[0] else .5
        self.outputStates.append([empty])

        return x, y

    def getGameAsBoardStates(self, savedGame):
        game = go.Go()

        self.index = 0

        game.begin(lambda state: self.aiStep(savedGame, state),
                 lambda state: self.aiStep(savedGame, state))

    def inceptionFunctional(self, input):
        t1 = Convolution2D(32, 1, 1, border_mode='same')(input)
        tower_1 = Convolution2D(32, 3, 3, border_mode='same')(t1)

        t2 = Convolution2D(32, 1, 1, border_mode='same')(input)
        t2 = Convolution2D(32, 3, 3, border_mode='same')(t2)
        tower_2 = Convolution2D(32, 3, 3, border_mode='same')(t2)

        t3 = MaxPooling2D((3, 3), strides=(1, 1), border_mode='same')(input)
        tower_3 = Convolution2D(32, 1, 1, border_mode='same')(t3)

        tower_4 = Convolution2D(32, 1, 1, border_mode='same')(input)

        return merge([tower_1, tower_2, tower_3, tower_4, input], mode='concat', concat_axis=1)

    def denseBlock(self, x, num_layers, nb_filter, growth_rate, weight_decay=1E-4):

        layers = []

        for i in range(num_layers):
            x = Convolution2D(nb_filter, 1, 1, init='he_uniform', border_mode='same', bias=False, W_regularizer=l2(weight_decay))(x)

            x = BatchNormalization(mode=0, axis=1, gamma_regularizer=l2(weight_decay), beta_regularizer=l2(weight_decay))(x)
            x = Activation('relu')(x)

            x = Convolution2D(nb_filter, 3, 3, init="he_uniform", border_mode="same", bias=False, W_regularizer=l2(weight_decay))(x)
            x = Activation("relu")(x)

            layers.append(x)

            if len(layers) > 1:
                x = merge(layers, mode='concat', concat_axis=1)

            nb_filter += growth_rate

        return x

    def makeModelFunctionalDense(self, input):
        weight_decay = 1E-4

        x = Convolution2D(32, 3, 3, border_mode='valid')(input)
        x = self.denseBlock(x,6,16,10)

        x = BatchNormalization(mode=0, axis=1, gamma_regularizer=l2(weight_decay), beta_regularizer=l2(weight_decay))(x)
        x = AveragePooling2D((2, 2), strides=(2, 2))(x)

        x = self.denseBlock(x, 8, 16, 10)

        x = Dropout(.2)(x)

        x = GlobalAveragePooling2D((3,3))(x)

#        x = Flatten()(x)
        x = Dense(self.nb_output, activation='softmax')(x)

        self.model = Model(input=input, output=x)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer='adadelta',
                           metrics=['accuracy'])

    def makeModelFunctionalInception(self, input):
        x = self.inceptionFunctional(input)
        x = advanced_activations.SReLU()(x)
        x = Convolution2D(32, 3, 3, border_mode='valid')(x)
        x = MaxPooling2D(pool_size=self.pool_size)(x)
        x = Flatten()(x)
        x = Dense(512, activation='relu')(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(.2)(x)
        x = Dense(self.nb_output, activation='softmax')(x)

        self.model = Model(input=input, output=x)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer='adadelta',
                           metrics=['accuracy'])

    def makeModelFunctional(self, input):
        x = Convolution2D(32, 1, 1, activation='linear', border_mode='valid')(input)
        x = Convolution2D(64, 5, 5, activation='relu', border_mode='same')(x)
        x = Convolution2D(64, 3, 3, activation='relu', border_mode='valid')(x)
        x = Flatten()(x)
        x = Dense(512, activation='relu')(x)
        x = Dense(256, activation='relu')(x)
        x = Dense(81, activation='relu')(x)
        x = Reshape((1, 9, 9))(x)

        x = Convolution2D(64, 3, 3, activation='relu', border_mode='same')(x)
        x = Dropout(.15)(x)
        x = Convolution2D(32, 1, 1, activation='relu', border_mode='same')(x)
        x = Convolution2D(1, 1, 1, activation='sigmoid', border_mode='valid')(x)

        self.model = Model(input=input, output=x)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer='adadelta',
                           metrics=['accuracy'])


    def makeModelFunctionalSimple(self, input):
        x = Convolution2D(64, 3, 1, border_mode='valid')(input)
        x = Convolution2D(64, 1, 3, border_mode='valid')(x)
        x = advanced_activations.SReLU()(x)
        x = MaxPooling2D(pool_size=self.pool_size)(x)
        x = Flatten()(x)
        x = Dense(512, activation='relu')(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(.2)(x)
        x = Dense(self.nb_output, activation='softmax')(x)

        self.model = Model(input=input, output=x)
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

    def getModelDataFormat2D(self, inputStates, outputStates):
        take = int(len(inputStates)*.8)

        x_train = inputStates[:take].astype('float32')
        x_test = inputStates[take:].astype('float32')
        y_train = (outputStates[:take]).astype('float32')
        y_test = (outputStates[take:]).astype('float32')

        print('X_train shape:', x_train.shape)
        print(x_train.shape[0], 'train samples')
        print(x_test.shape[0], 'test samples')

        return x_train, x_test, y_train, y_test

    def trainOnGames(self, savedGames):
        for savedGame in savedGames:
            self.getGameAsBoardStates(savedGame)

        x_train, x_test, y_train, y_test = self.getModelDataFormat(np.array(self.inputStates), np.array(self.outputStates))

        input_shape = (1, self.rows, self.cols)
        inputLayer = Input(shape=input_shape)

        self.makeModelFunctionalDense(inputLayer)

        model_json = self.model.to_json()
        with open(savepath+".json", "w") as json_file:
            json_file.write(model_json)

        checkpointer = ModelCheckpoint(filepath=savepath+".h5", verbose=1, save_best_only=True)
        self.model.fit(x_train, y_train, batch_size=self.batch_size, nb_epoch=self.nb_epoch, verbose=1, validation_data=(x_test, y_test), callbacks=[checkpointer])
        score = self.model.evaluate(x_test, y_test, verbose=0)
        print('Test score:', score[0])
        print('Test accuracy:', score[1])

        # serialize weights to HDF5
        self.model.save_weights(savepath+".h5")

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

dir_path = os.path.dirname(os.path.realpath(__file__))+"\\openblas"
if os.name == "nt":
    os.environ["PATH"] += os.pathsep + dir_path
    theano.config.blas.ldflags = "-L"+dir_path+" -lopenblas"
    print('blas.ldflags=', theano.config.blas.ldflags)

savepath = "savedNetwork-gpu"
tnt = NeuralTrainer()
tnt.loadFile()