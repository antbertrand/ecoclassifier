# EcoClassifier

Classification of different types of plastic.

## Getting Started


To test the classification on some images, clone this repo on your machine


### Downloading the dataset

The dataset is often updated. These instuctions will get you the dataset with the latest images :

#### DL / Install the cloudlabel client

Cloudlabel is an interactive client where the labeling is done. We will use it to download the dataset.

```
git clone https://github.com/numericube/cloudlabel-client.git
git checkout develop
virtualenv -p /usr/local/bin/python3 ve_cloudlabel_client
source ./ve_cloudlabel_client/bin/activate
pip install -r ./requirements.txt
pip install -e .
```

#### DL the dataset

```
cd <target directory>
cloudlabel-cli --project majurca-ecoclassifier --api-url=http://52.143.156.104/api/v1 sync
# Wait a bit if it download gets stuck. Try again if error : "cannot join current thread".
```


### Downloading the trained models (.h5 files)

The models are stored on an Azure blob storage.
Connect to it with Microsoft Azure Explorer, with the Shared Access Signature URL :

*https://majurca.blob.core.windows.net/weights?st=2019-04-23T07%3A40%3A38Z&se=2020-04-24T07%3A40%3A00Z&sp=rwdl&sv=2018-03-28&sr=c&sig=iNQADtLxJF%2Fs9H1NXG%2BM2qCFKhHF8I5pVgY175yE0XE%3D*


### Prerequisites

What things you need to run the classification program:

* [Keras](https://www.pyimagesearch.com/2016/11/14/installing-keras-with-tensorflow-backend/) - The deep learning library used
* [Pandas](https://pandas.pydata.org/pandas-docs/stable/install.html)
* [Scikit-learn](https://scikit-learn.org/stable/install.html)


<br /><br />


## Deployment






## Model evaluation

The models are evaluated on an holdout Test set.

## DIfferent architectures performances comparison on the 3 classes classification

Networks                      | AlexNet     |     VGG16   |     InceptionV3   |   Not pretrained Simple CNN
------------------------------|-------------|-------------|-------------------|-----------------------------
Global Accuracy               |   ?         |   96,6%     |   92,4%           |     90,1%
Number of params                    |     61M     |     138M    |     23M    | ?
Prediction time, single image (CPU) |   ? (faster than vgg16)   |   0.64s   |   ?   | 0.07s

## Results with VGG16

#### 3 classes : godet-vide vs pet-clair vs pet-fonce

![confmat_3classes](screenshots/confmat_3class.jpg)

<br />
<br />

#### 4 classes : godet-vide vs pe-hd-opaque vs pet-clair vs pet-fonce

![confmat_4classes](screenshots/confmat_4class.jpg)
