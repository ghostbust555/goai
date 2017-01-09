from keras.engine import Model
from keras.engine import merge
from keras.layers import Convolution2D, Activation, AveragePooling2D, UpSampling2D, Dropout, BatchNormalization, GlobalAveragePooling2D, Dense, MaxPooling2D, advanced_activations, \
    Flatten
from keras.regularizers import l2

from neuraltrainer import NeuralTrainer

# 27% accuracy

class InceptionNet(NeuralTrainer):
    def inceptionFunctional(self, input):
        t1 = Convolution2D(32, 1, 1, border_mode='same')(input)
        tower_1 = Convolution2D(32, 3, 3, border_mode='same')(t1)

        t2 = Convolution2D(32, 1, 1, border_mode='same')(input)
        t2 = Convolution2D(32, 3, 3, border_mode='same')(t2)
        tower_2 = Convolution2D(32, 3, 3, border_mode='same')(t2)

        t3 = MaxPooling2D((3, 3), strides=(1, 1), border_mode='same')(input)
        tower_3 = Convolution2D(32, 1, 1, border_mode='same')(t3)

        tower_4 = Convolution2D(32, 1, 1, border_mode='same')(input)

        x = merge([tower_1, tower_2, tower_3, tower_4], mode='concat', concat_axis=1)

        return merge([input, x], mode="sum")

    def makeModelFunctionalInception(self, input):
        x = Convolution2D(128, 1, 1)(input)
        x = self.inceptionFunctional(x)
        x = advanced_activations.SReLU()(x)
        x = Convolution2D(32, 3, 3, border_mode='valid')(x)
        x = Flatten()(x)
        x = Dense(512, activation='relu')(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(.2)(x)
        x = Dense(self.nb_output, activation='softmax')(x)

        self.model = Model(input=input, output=x)
        self.model.compile(loss='categorical_crossentropy',
                           optimizer='adadelta',
                           metrics=['accuracy'])

    def makeModel(self, input):
        self.makeModelFunctionalInception(input)


dn = InceptionNet()
dn.makeModel(dn.inputLayer)
dn.trainOnGames("savedNetwork-inceptionnet")