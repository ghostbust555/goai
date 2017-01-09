from keras.engine import Model
from keras.engine import merge
from keras.layers import Convolution2D, Activation, AveragePooling2D, UpSampling2D, Dropout, BatchNormalization, GlobalAveragePooling2D, Dense
from keras.regularizers import l2

from neuraltrainer import NeuralTrainer

# 29% accuracy

class DenseNet(NeuralTrainer):
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

    def makeModelDense(self, input):
        weight_decay = 1E-4

        x = Convolution2D(32, 3, 3, border_mode='valid')(input)
        x = self.denseBlock(x, 6, 16, 10)

        x = BatchNormalization(mode=0, axis=1, gamma_regularizer=l2(weight_decay), beta_regularizer=l2(weight_decay))(x)
        x = AveragePooling2D((2, 2), strides=(2, 2))(x)

        x = self.denseBlock(x, 8, 16, 10)

        x = Dropout(.2)(x)

        x = GlobalAveragePooling2D((3, 3))(x)

        x = Dense(self.nb_output, activation='softmax')(x)

        self.model = Model(input=input, output=x)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer='adadelta',
                           metrics=['accuracy'])

    def makeModel(self, input):
        self.makeModelDense(input)


dn = DenseNet()
dn.makeModel(dn.inputLayer)
dn.trainOnGames("savedNetwork-densenet")