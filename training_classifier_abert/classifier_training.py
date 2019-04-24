import json
import os
import PIL
import PIL.Image
from IPython.display import display
from PIL import Image

import matplotlib.pyplot as plt


import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split

from collections import Counter


from keras_preprocessing.image import ImageDataGenerator
from keras.preprocessing import image
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.models import Sequential, Model
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D
from keras_preprocessing.image import ImageDataGenerator
from keras.layers import Dense, Activation, Flatten, Dropout, Input

from keras import optimizers
from keras import metrics

from keras.models import load_model
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
#test

def test():
    return True


def getData():
    """ Function getData() uses the JSON info to select the dataset

    Parameters:
    None

    Returns:
    files : list
        List of the filenames of all the dataset
    labels : list
        List of the labels corrsponding to im_path

    """

    filename = "./dataset/majurca-ecoclassifier-assets.json"

    files = []
    labels = []

    # k will count the amount of ignored images
    k = 0

    # Read JSON data into the datastore variable
    if filename:
        with open(filename, "r") as f:
            list_info = json.load(f)

    str_filter = "192-168-0-31"

    for dict in list_info:

        # Condition that keeps only images from top camera
        if str_filter in dict["path"]:

            # Condition that keeps only the concerned labels
            if dict["tag_slugs"] != [] and dict["tag_slugs"] in [
                ["godet-vide"],
                ["pet-fonce"],
                ["pet-clair"],
            ]:

                labels.append(dict["tag_slugs"][0])
                str = dict["thumbnail_320x200_path"]
                # Changes character in filename / Depending on OS
                str2 = str.replace(":", "_")
                files.append(str2)

            else:
                # print('no label',dict['path'])
                k = k + 1
        else:
            # print('wrong camera',dict['path'])
            k = k + 1

    print("{} images were ignored".format(k))

    return files, labels


def splitData(X, y):
    """ Function splitData(X,y) creates a separated Test Set

    Parameters:
    X : list
        List of the filenames of the whole dataset
    y : list
        List of the labels of the whole dataset

    Returns:
    X_tv : list
        List of the filenames of the Training + Validation set (aka tv)
    y_tv : list
        List of the labels corresponding to the files in X_tv
    X_test : list
        List of the filenames that will be used to test/evaluate our model
    y_test : list
        List of the labels corresponding to the files in X_test

    """

    output_dir = "./dataset_split"

    # Splits the dataset in 2 with Stratify ( keeps classes repartition)
    X_tv, X_test, y_tv, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Create folder for the test and training split
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        os.mkdir(output_dir + "/test")
        os.mkdir(output_dir + "/train")

        # Copying files into test and train folder
        for file in X_test:
            os.system("cp ./dataset/" + file + " " + output_dir + "/test/" + file)
        for file in X_tv:
            os.system("cp ./dataset/" + file + " " + output_dir + "/train/" + file)

    # If the folder already exists, doesn't copy
    else:
        print("Warning: output dir {} already exists".format(output_dir))

    return X_tv, X_test, y_tv, y_test


def getModelVGG16():
    """ Function getModelVGG16() builds and compiles the model

    Parameters:
    None

    Returns:
    model : 
        Model ready to be trained

    """

    # Loads the VGG16 pre-trained network
    base_model = VGG16(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    print("Model loaded.")

    # Builds a classifier model to put on top of the convolutional model
    top_model = Sequential()
    top_model.add(Flatten(input_shape=base_model.output_shape[1:]))
    top_model.add(Dense(256, activation="relu"))
    top_model.add(Dropout(0.5))
    top_model.add(Dense(3, activation="sigmoid"))

    # Adds the model on top of the convolutional base
    model = Model(inputs=base_model.input, outputs=top_model(base_model.output))

    # Sets the first 10 layers
    # to non-trainable (weights will not be updated)
    for layer in model.layers[:10]:
        layer.trainable = False

    # Compiles the model with a Adam optimizer
    model.compile(
        loss="categorical_crossentropy",
        optimizer=optimizers.Adam(lr=1e-5),
        metrics=["accuracy"],
    )

    return model


def train(X, y, model):
    """ Function train(X,y) prepares the data and trains the model

    Parameters:
    X : list
        List of the filenames of the Training+Validation dataset
    y : list
        List of the labels of the Training+Validation dataset
    model :
        Model that will be trained

    Returns:
    model_trained:
        Trained model
    history:
        Keras history file that contains all the informations of the training

    """

    HEIGHT = 224  # 224 for resnet50 and VGG16 / 299 for InceptionV3
    WIDTH = 224  # 224 for resnet50 and VGG16 / 299 for inceptionV3
    BATCH_SIZE = 16
    EPOCHS = 6

    CATEGORIES = ["godet-vide", "pet-clair", "pet-fonce"]

    # Data augmentation parameters
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        featurewise_std_normalization=True,
        rotation_range=0,
        horizontal_flip=False,
        vertical_flip=False,
    )

    validation_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

    # DATA PREPARATION
    # With .flow_from_dataframe()
    n_train_samples = len(X) * 0.8
    n_val_samples = len(X) * 0.2
    target_labels = y

    datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input, validation_split=0.2
    )
    # Conversion of the 2 lists in 1 pandas dataframe
    dataset_info = {"filename": X, "class": y}
    dataframe = pd.DataFrame(dataset_info)

    train_generator = datagen.flow_from_dataframe(
        dataframe,
        directory="./dataset_split/train/",
        subset="training",
        class_mode="categorical",
        classes=target_labels,
        target_size=(HEIGHT, WIDTH),
        batch_size=BATCH_SIZE,
    )

    validation_generator = datagen.flow_from_dataframe(
        dataframe,
        directory="./dataset_split/train/",
        subset="validation",
        class_mode="categorical",
        classes=target_labels,
        target_size=(HEIGHT, WIDTH),
        batch_size=BATCH_SIZE,
    )

    # Starts training
    history = model.fit_generator(
        train_generator,
        steps_per_epoch=n_train_samples // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=validation_generator,
        validation_steps=n_val_samples // BATCH_SIZE,
    )

    return model, history


def plotHistory(history):
    """ Function plotHistory(history) plots the training loss/acc evolution

    Parameters:
    history: Keras history
        Contains all the info o the training

    Returns:
    None

    """

    # Summarize history for accuracy
    plt.plot(history.history["acc"])
    plt.plot(history.history["val_acc"])
    print(history.history["val_acc"][-1])
    plt.title("model accuracy")
    plt.ylabel("accuracy")
    plt.xlabel("epoch")
    plt.legend(["train", "validation"], loc="upper left")
    plt.show()

    # Summarize history for loss
    plt.plot(history.history["loss"])
    plt.plot(history.history["val_loss"])
    plt.title("model loss")
    plt.ylabel("loss")
    plt.xlabel("epoch")
    plt.legend(["train", "validation"], loc="upper left")
    plt.show()


def evaluate(X_test, y_test):
    """ Function evaluate(X_test, y_test) evaluattes the trained model on the holdout Test Set

    Parameters:
    X_test: List
        Contains all the filenames of the test set
    y_test: List
        Contains all the labels corresponding to the files in X_test

    Returns:
    None

    """

    TEST_DIR = "./dataset_split/test"
    HEIGHT = 224  # 224 for resnet50 and VGG16 / 299 for InceptionV3
    WIDTH = 224  # 224 for resnet50 and VGG16 / 299 for inceptionV3
    BATCH_SIZE = 16

    # DATA PREPARATION
    test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

    # Conversion of the 2 lists in 1 pandas dataframe
    test_info = {"id": X_test, "label": y_test}
    testdf = pd.DataFrame(test_info)

    # Data preparation
    test_generator = test_datagen.flow_from_dataframe(
        dataframe=testdf,
        directory="./dataset_split/test/",
        x_col="id",
        y_col="label",
        batch_size=BATCH_SIZE,
        shuffle=False,
        class_mode="categorical",
        target_size=(HEIGHT, WIDTH),
    )

    model = load_model("vgg16_v5.h5")

    probabilities = model.predict_generator(test_generator, len(test_generator))

    # The true labels
    y_true = test_generator.classes

    # The predicted labels
    y_pred = probabilities.argmax(axis=-1)

    # Plots confusion matrix
    print(confusion_matrix(y_true, y_pred))

    # Computes global accuracy
    acc = accuracy_score(y_true, y_test)
    print(acc)


def main():

    # Gives the whole dataset
    files, labels = getData()

    # Splits the dataset in two / Creates the holdout Test set
    X_tv, X_test, y_tv, y_test = splitData(files, labels)

    # Builds the model
    model = getModelVGG16()

    # Starts training
    model_trained, history = train(X_tv, y_tv, model)
    model_trained.save("vgg16_v5.h5")

    # PLots Loss and Accuracy evolution
    plotHistory(history)

    # Evaluates the trained network on test set
    evaluate(X_test, y_test)


main()
