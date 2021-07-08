## Imports libs
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ["SM_FRAMEWORK"] = "tf.keras"

from tensorflow import keras
import segmentation_models as sm

import os
import sys

# If you like to speed up training process with GPU, first install PlaidML and then uncomment the following line.
# Otherwise it will fallback to tensorflow.

#os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"
#os.environ["SM_FRAMEWORK"] = "tf.keras"
#import tensorflow as tf
#from tensorflow import keras
#from tensorflow.keras import layers

from tensorflow.keras import optimizers
from tensorflow.keras.layers import Dropout, Flatten, Dense, Activation, BatchNormalization
from keras.layers.convolutional import Convolution2D, MaxPooling2D, Conv2D
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint

DEV = False
argvs = sys.argv
argc = len(argvs)

if argc > 1 and (argvs[1] == "--development" or argvs[1] == "-d"):
  DEV = True

if DEV:
  epochs = 10
else:
  epochs = 20 #sonst 1000

# BEFORE STARTING TRAINING YOU NEED TO MANUALLY TAKE 20 PERCENENT OF THE TRAINING DATA AND PUT IT INTO VALIDATION FOLDER
# I was too lazy to do it in the code.

train_data_dir = './data/train/'
validation_data_dir = './data/validation/'

# Input the size of your sample images
img_width, img_height = 150, 150
# Enter the number of samples, training + validation
nb_train_samples = 15974
nb_validation_samples = 1991
nb_filters1 = 32
nb_filters2 = 32
nb_filters3 = 64
conv1_size = 3
conv2_size = 2
conv3_size = 5
pool_size = 2
# We have 2 classes, buy and sell
classes_num = 3
batch_size = 128
lr = 0.001
chanDim =3

model = Sequential()
model.add(Convolution2D(nb_filters1, conv1_size, conv1_size, padding ='same', input_shape=(img_height, img_width , 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(pool_size, pool_size)))

model.add(Convolution2D(nb_filters2, conv2_size, conv2_size, padding ="same"))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(pool_size, pool_size)))

model.add(Convolution2D(nb_filters3, conv3_size, conv3_size, padding ='same'))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(pool_size, pool_size)))

model.add(Flatten())
model.add(Dense(1024))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(classes_num, activation='softmax'))

model.summary()
model.compile(loss='categorical_crossentropy',
                      optimizer=optimizers.RMSprop(),
                      metrics=['accuracy'])

train_datagen = ImageDataGenerator(
    #rescale=1. / 255,
    horizontal_flip=False)

test_datagen = ImageDataGenerator(
    #rescale=1. / 255,
    horizontal_flip=False)

train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_height, img_width),
    #shuffle=True,
    batch_size=batch_size,
    class_mode='categorical'
)

validation_generator = test_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    #shuffle=True,
    class_mode='categorical')

"""
Tensorboard log
"""
target_dir = "./models/weights-improvement-{epoch:02d}.hdf5"
print(target_dir)
#if not os.path.exists(target_dir):
#  os.mkdir(target_dir)
model.save('./src/models/model.h5')
model.save_weights('./src/models/weights.h5')

checkpoint = ModelCheckpoint(target_dir, monitor='val_accurancy', verbose=1, save_best_only=True, mode='max')
callbacks_list = [checkpoint]

model.fit(
    train_generator,
    steps_per_epoch=nb_train_samples//batch_size,
    epochs=epochs,
    shuffle=True,
    #validation_data=validation_generator,
    validation_split=0.1,
    callbacks=callbacks_list,
    validation_steps=nb_validation_samples//batch_size)


