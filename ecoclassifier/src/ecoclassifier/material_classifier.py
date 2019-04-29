#!/usr/bin/env python3
# encoding: utf-8
"""
classifier.py

Created by Pierre-Julien Grizel et al.
Copyright (c) 2016 NumeriCube. All rights reserved.

Main Deep Learning classifier structure
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

import os
import hashlib
import logging
import base64

from azure.storage.blob import BlockBlobService
from keras.models import load_model

import numpy as np
import cv2

# Configure logging
logger = logging.getLogger(__name__)
logger.info("Starting Ecoclassifier module.")

# Various contants
MODEL_BLOB = "vide_pehd_petc_petf-vgg16-20192304162500.h5"
MODEL_CONTAINER = "weights"
# BLOB_SAS_URL = "https://majurca.blob.core.windows.net/?sv=2018-03-28&ss=b&srt=sco&sp=rl&se=2029-04-29T22:53:30Z&st=2019-04-29T14:53:30Z&spr=https&sig=owBhOFWBlmVIpby8B%2FSBoOrsNXLZOWxj5IsPwkLOUY4%3D"
MODEL_CONNECTION_STRING = "BlobEndpoint=https://majurca.blob.core.windows.net/;QueueEndpoint=https://majurca.queue.core.windows.net/;FileEndpoint=https://majurca.file.core.windows.net/;TableEndpoint=https://majurca.table.core.windows.net/;SharedAccessSignature=sv=2018-03-28&ss=b&srt=sco&sp=rl&se=2029-04-29T22:53:30Z&st=2019-04-29T14:53:30Z&spr=https&sig=owBhOFWBlmVIpby8B%2FSBoOrsNXLZOWxj5IsPwkLOUY4%3D"
MODEL_PATH = "/var/majurca/weights/classifier.h5"


class MaterialClassifier(object):
    """This is the main classifier model, taking care of downloading additional data if necessary
    (ie. model weights!)
    """

    model = None

    HEIGHT = 224
    WIDTH = 224

    CLASS_GODET_VIDE = 0
    CLASS_PE_HD_OPAQUE = 1
    CLASS_PET_CLAIR = 2
    CLASS_PET_FONCE = 3
    # in [0, 1, 2, 3] corresponding to ['godet-vide', 'pe-hd-opaque','pet-clair', 'pet-fonce']

    def classify(self, image):
        """Predict from a NUMPY array
        """
        # Prepare image
        img_target = cv2.resize(
            image, dsize=(self.HEIGHT, self.WIDTH), interpolation=cv2.INTER_CUBIC
        )
        img_target = np.expand_dims(
            img_target, axis=0
        )  # correct shape for classification

        # Classify it
        klass = self.model.predict(img_target)
        klass = klass.argmax(axis=-1)  # taking index of the maximum %
        return klass[0]

    # model = load_model('vgg16_v3.h5')
    #
    # im_path = './dataset/wsEN4iv2SliFUuYNXIM-5Q_0b9FT9bgTKSFE4NaMtMCwA_320x200.png'
    #
    # img = image.load_img(im_path, target_size=(HEIGHT, WIDTH)) #resize
    # img = image.img_to_array(img)
    # img = np.expand_dims(img, axis=0)# correct shape for classification
    #
    # print(classify(img,model))

    @staticmethod
    def _read_file_md5(fname):
        """Read md5 from file
        Taken from: https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
        """
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as fcontent:
            for chunk in iter(lambda: fcontent.read(4096), b""):
                hash_md5.update(chunk)
        return base64.b64encode(hash_md5.digest()).decode("ascii")

    def __init__(
        self,
        model_connection_string=MODEL_CONNECTION_STRING,
        model_container=MODEL_CONTAINER,
        model_blob=MODEL_BLOB,
        model_path=MODEL_PATH,
    ):
        """Load initial model if not present yet
        """
        # Check if file exists / is fresh
        download_it = True
        if os.path.isfile(model_path):
            # File exists? Retreive online md5 from Azure
            target_blob_service = BlockBlobService(
                connection_string=model_connection_string
            )
            blob = target_blob_service.get_blob_properties(
                container_name=model_container, blob_name=model_blob
            )
            blob_md5 = blob.properties.content_settings.content_md5

            # Read file md5 & compare
            file_md5 = self._read_file_md5(model_path)
            if file_md5 == blob_md5:
                download_it = False

        # Download if necessary
        if download_it:
            # Create target path if necessary
            os.makedirs(os.path.split(model_path)[0], exist_ok=True)

            # Download
            logger.info("Downloading latest model version: %s", model_blob)
            target_blob_service = BlockBlobService(
                connection_string=model_connection_string
            )
            target_blob_service.get_blob_to_path(
                container_name=model_container,
                blob_name=MODEL_BLOB,
                file_path=model_path,
            )

        # Load model
        self.model = load_model(model_path)
