# EcoClassifier

Classification of different types of plastic.


## Downloading the dataset

The dataset is often updated. These instuctions will get you the dataset with the latest images :

### DL / Install the cloudlabel client

Cloudlabel is an interactive client where the labeling is done. We will use it to download the dataset.

```
git clone https://github.com/numericube/cloudlabel-client.git
git checkout develop
virtualenv -p /usr/local/bin/python3 ve_cloudlabel_client
source ./ve_cloudlabel_client/bin/activate
pip install -r ./requirements.txt
pip install -e .
```

### DL the dataset

```
cd <target directory>
cloudlabel-cli --project majurca-ecoclassifier --api-url=http://52.143.156.104/api/v1 sync
# Wait a bit if it download gets stuck. Try again if error : "cannot join current thread".
```

To test the classification on some images, clone this repo on your machine


## Downloading the trained models (.h5 files)

The models are stored on an Azure blob storage. 
Connect to it with Microsoft Azure Explorer, with the Shared Access Signature URL :

*https://majurca.blob.core.windows.net/weights?st=2019-04-23T07%3A40%3A38Z&se=2020-04-24T07%3A40%3A00Z&sp=rwdl&sv=2018-03-28&sr=c&sig=iNQADtLxJF%2Fs9H1NXG%2BM2qCFKhHF8I5pVgY175yE0XE%3D*

### Prerequisites

What things you need to run the classification program:

* [Keras](https://www.pyimagesearch.com/2016/11/14/installing-keras-with-tensorflow-backend/) - The deep learning library used
* [Pandas](https://pandas.pydata.org/pandas-docs/stable/install.html) 
* [Scikit-learn](https://scikit-learn.org/stable/install.html)



## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds


## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)


