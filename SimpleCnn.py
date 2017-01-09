from keras.engine import Model
from keras.engine import merge
from keras.layers import Convolution2D, Activation, AveragePooling2D, UpSampling2D, Dropout, BatchNormalization, GlobalAveragePooling2D, Dense, Flatten, \
    MaxPooling2D
from keras.regularizers import l2

from neuraltrainer import NeuralTrainer

#

class SimpleCnn(NeuralTrainer):
    def makeModel(self, input):
        x = Convolution2D(64, 3, 3, activation='relu', border_mode='same')(input)
        x = MaxPooling2D((2,2))(x)
        x = Convolution2D(64, 3, 3, activation='relu', border_mode='valid')(x)
        x = Flatten()(x)
        x = Dense(512, activation='relu')(x)
        x = Dense(256, activation='relu')(x)
        x = Dense(81, activation='relu')(x)

        self.model = Model(input=input, output=x)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer='adadelta',
                           metrics=['accuracy'])


dn = SimpleCnn()
dn.makeModel(dn.inputLayer)
dn.trainOnGames("savedNetwork-cnn")