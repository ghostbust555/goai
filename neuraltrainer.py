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

    savepath = ""

    batch_size = 150
    nb_output = boardSize*boardSize
    nb_epoch = 100
    rows, cols = boardSize, boardSize

    totalInputs = []
    totalOutputs = []

    model = None

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "\\openblas"
        if os.name == "nt":
            os.environ["PATH"] += os.pathsep + dir_path
            theano.config.blas.ldflags = "-L" + dir_path + " -lopenblas"
            print('blas.ldflags=', theano.config.blas.ldflags)

        self.savepath = "savedNetwork-gpu"

        self.loadFile()

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

                    count += 1
                else:
                    game += line
        shuffle(savedGames)
        self.setupTrainingData(savedGames)

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


    def makeModel(self, input):
        pass

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

    def setupTrainingData(self, savedGames):
        for savedGame in savedGames:
            self.getGameAsBoardStates(savedGame)

        self.x_train, self.x_test, self.y_train, self.y_test = self.getModelDataFormat(np.array(self.inputStates), np.array(self.outputStates))

        input_shape = (1, self.rows, self.cols)
        self.inputLayer = Input(shape=input_shape)

        self.savedGames = savedGames

    def trainOnGames(self, savepath):

        model_json = self.model.to_json()
        with open(savepath+".json", "w") as json_file:
            json_file.write(model_json)

        checkpointer = ModelCheckpoint(filepath=savepath+".h5", verbose=1, save_best_only=True)
        self.model.fit(self.x_train, self.y_train, batch_size=self.batch_size, nb_epoch=self.nb_epoch, verbose=1, validation_data=(self.x_test, self.y_test), callbacks=[checkpointer])
        score = self.model.evaluate(self.x_test, self.y_test, verbose=0)
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


tnt = NeuralTrainer()
