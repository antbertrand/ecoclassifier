import json
import os

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np

#from alexnet_model import create_alexnet

from sklearn.model_selection import train_test_split
from collections import Counter

from keras_preprocessing.image import ImageDataGenerator
from keras.layers import Dense, Activation, Flatten, Dropout
from keras.models import Sequential, Model
from keras.optimizers import SGD, Adam
#from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.applications.vgg16 import VGG16, preprocess_input
#from convnetskeras.convnets import preprocess_image_batch, convnet



def getData():

    filename = './dataset/majurca-ecoclassifier-assets.json'

    im_path = []
    labels = []
    k=0

    #Read JSON data into the datastore variable
    if filename:
        with open(filename, 'r') as f:
            list_info = json.load(f)

    str_filter = '192-168-0-31' # to filter certain files

    #print(list_info[2443]['id'])
    #print(len(list_info))

    for dict in list_info:
        #print(k)
        if str_filter in dict['path']:
            if dict['tag_slugs'] != [] and dict['tag_slugs'] in [['godet-vide'], ['pet-fonce'], ['pet-clair']]:

                labels.append(dict['tag_slugs'][0])
                im_path.append(dict['thumbnail_320x200_path'])

            else:
                #print('no label',dict['path'])
                k=k+1
        else:
            #print('wrong camera',dict['path'])
            k=k+1

    print('{} images were ignored'.format(k))
    print(len(im_path),len(labels))
    return im_path, labels





def splitData(X,y):

    output_dir = './dataset_split'
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    #Create folder for the test and training split
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        os.mkdir(output_dir + '/test')
        os.mkdir(output_dir + '/train')
    else:
        print("Warning: output dir {} already exists".format(output_dir))

    #Copying files into test and train folder
    label_count_test = []
    label_count_train = []

    for file in X_test:
        #file = file.replace(':','/')
        os.system('cp ./dataset/'+ file + ' ' + output_dir + '/test/' + file)

    for file in X_train:
        #file = file.replace(':','/')
        os.system('cp ./dataset/'+ file + ' ' + output_dir + '/train/' + file)

    #print(Counter(y_train), Counter(y_test))

    return X_train, X_test, y_train, y_test





def splitValidation(X,y):

    X_train, X_vali, y_train, y_vali = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    return X_train, X_vali, y_train, y_vali




def train(X_train, y_train, X_vali, y_vali):

    TRAIN_DIR = "./dataset/train"
    VALIDATION_DIR =  "./dataset/validation"


    HEIGHT = 224
    WIDTH = 224
    BATCH_SIZE = 32

    CATEGORIES = ["godet-vide","pet-clair","pet-fonce"]


    #DATA AUGMENTATION
    train_datagen =  ImageDataGenerator(
            preprocessing_function=preprocess_input,
            featurewise_std_normalization= True,
            rotation_range=0,
            horizontal_flip=False,
            vertical_flip=False
        )

    validation_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)


    #DATA PREPARATION


    # WITH FLOW FROM DATAFRAME
    train_info = {'id':X_train,'label':y_train}
    vali_info = {'id':X_vali,'label':y_vali}

    traindf = pd.DataFrame(train_info)
    validf = pd.DataFrame(vali_info)

    train_generator=validation_datagen.flow_from_dataframe(
        dataframe=traindf,
        directory="./train/",
        x_col="id",
        y_col="label",
        subset="training",
        batch_size=BATCH_SIZE,
        seed=42,
        shuffle=True,
        class_mode="categorical",
        target_size=(HEIGHT,WIDTH))

    valid_generator=train_datagen.flow_from_dataframe(
        dataframe=validf,
        directory="./train/",
        x_col="id",
        y_col="label",
        subset="validation",
        batch_size=BATCH_SIZE,
        seed=42,
        shuffle=True,
        class_mode="categorical",
        target_size=(HEIGHT,WIDTH))

    #MODEL CREATION
    #base_model = ResNet50(include_top = False, weights = "imagenet",input_shape=(HEIGHT, WIDTH, 3))
    base_model = VGG16(weights='imagenet', include_top=False)
    #base_model = convnet('alexnet',weights_path="weights/alexnet_weights.h5", heatmap=False)

    #WITH AlEXNET
    '''
    model = create_alexnet()
    #Adding alexnet prtrained weights
    model.load_weights('weights/alexnet_weights.h5')
    model.compile(optimizer=sgd, loss='mse')
    '''

    dropout = 0.5
    fc_layers = [HEIGHT,WIDTH]
    num_classes = len(CATEGORIES)

    #Freezing the weights
    for layer in base_model.layers:
            layer.trainable = True

    x = base_model.output
    x = Flatten()(x)
    for fc in fc_layers:
        # New FC layer, random initialisation
        x = Dense(fc, activation='relu')(x)
        x = Dropout(dropout)(x)

    # New softmax layer
    predictions = Dense(num_classes, activation='softmax')(x)

    finetune_model = Model(inputs=base_model.input, outputs=predictions)


    #TRAINING
    NUM_EPOCHS = 20
    num_train_images = len(train_generator)

    adam = Adam(lr=0.0001)
    finetune_model.compile(adam, loss='categorical_crossentropy', metrics=['accuracy'])



    history = finetune_model.fit_generator(train_generator, epochs=NUM_EPOCHS,
        steps_per_epoch=num_train_images // BATCH_SIZE,
        shuffle=True,
        validation_data=validation_generator,
        validation_steps=len(validation_generator.filenames) // BATCH_SIZE)



    finetune_model.save('model_gl_pl.h5')







def main():
    files_all, labels_all = getData()
    #print(type(files_all[3]),labels_all[3])
    X_try, X_test, y_try, y_test = splitData(files_all,labels_all)
    X_train, X_vali, y_train, y_vali = splitValidation(X_try, y_try)
    train(X_train, y_train, X_vali, y_vali)



main()
