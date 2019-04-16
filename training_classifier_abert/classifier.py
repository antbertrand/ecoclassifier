#!/usr/bin/env python
# encoding: utf-8
"""
classifier.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

Simple classifier
"""
from __future__ import unicode_literals

__author__ = ""
__copyright__ = "Copyright 2016, NumeriCube"
__credits__ = ["Pierre-Julien Grizel"]
__license__ = "CLOSED SOURCE"
__version__ = "TBD"
__maintainer__ = "Pierre-Julien Grizel"
__email__ = "pjgrizel@numericube.com"
__status__ = "Production"

import json
import os
import PIL
import PIL.Image
from IPython.display import display
from PIL import Image

import keras
from keras_preprocessing.image import ImageDataGenerator
from keras.applications.inception_v3 import preprocess_input, decode_predictions
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

# Import all the Keras machinery we need
from keras.applications.inception_v3 import InceptionV3
from keras.preprocessing import image
from keras.models import Model
from keras.models import load_model
from keras.layers import Dense, GlobalAveragePooling2D
from keras import backend as K
from keras import metrics
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense


def build_model():
    """Return the convnet model
    Build a simple CONVNET
    Like in https://blog.keras.io/building-powerful-image-classification-models-using-very-little-data.html
    """
    if K.image_data_format() == "channels_first":
        input_shape = (3, 224, 224)
    else:
        input_shape = (224, 224, 3)

    cnnmodel = Sequential()
    cnnmodel.add(Conv2D(32, (3, 3), input_shape=input_shape))
    cnnmodel.add(Activation("relu"))
    cnnmodel.add(MaxPooling2D(pool_size=(2, 2)))

    cnnmodel.add(Conv2D(32, (3, 3)))
    cnnmodel.add(Activation("relu"))
    cnnmodel.add(MaxPooling2D(pool_size=(2, 2)))

    cnnmodel.add(Conv2D(64, (3, 3)))
    cnnmodel.add(Activation("relu"))
    cnnmodel.add(MaxPooling2D(pool_size=(2, 2)))

    cnnmodel.add(Flatten())
    cnnmodel.add(Dense(64))
    cnnmodel.add(Activation("relu"))
    cnnmodel.add(Dropout(0.5))
    cnnmodel.add(Dense(3))
    cnnmodel.add(Activation("softmax"))

    cnnmodel.compile(
        loss="categorical_crossentropy",
        optimizer="rmsprop",
        metrics=["categorical_accuracy", "accuracy"],
    )

    return cnnmodel


def get_model():
    """Return our simple model
    """
    cnnmodel = load_model("simplecnn.h5")
    return cnnmodel


# Sample execution
with open("./dataset/majurca-ecoclassifier-assets.json", "r") as jsonf:
    assets = json.load(jsonf)
labels = set(("pet-clair", "pet-fonce", "godet-vide"))

# For each asset, try to predict
main_labels = [["godet-vide"], ["pet-clair"], ["pet-fonce"]]
cnnmodel = get_model()
good_labels = 0
n_labels = 0
for asset in assets:
    if not "192-168-0-31" in asset["path"]:
        continue
    if not asset["tag_slugs"]:
        continue
    if not asset["tag_slugs"] in main_labels:
        continue

    # Load image
    img = image.load_img(
        "./dataset/{}".format(asset["thumbnail_320x200_path"]), target_size=(224, 224)
    )
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    # x = preprocess_input(x)
    pred = cnnmodel.predict(x)
    pred = np.argmax(pred, axis=1)[0]
    tag_index = main_labels.index(asset["tag_slugs"])

    # List wrong labels, compute stats
    n_labels += 1
    if tag_index == pred:
        wrong = ""
        good_labels += 1
    else:
        wrong = "WRONG!!!"
    print(
        asset["thumbnail_320x200_path"], asset["tag_slugs"][0], tag_index, pred, wrong
    )

print("Good labels: %d%%" % (good_labels / n_labels * 100))
