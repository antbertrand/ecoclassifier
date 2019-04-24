

from keras.models import load_model
import numpy as np
from keras.preprocessing import image





def classify(im,model):
    """Classifies an image (np array or keras array)
        See here for difference:
        https://stackoverflow.com/questions/53718409/numpy-array-vs-img-to-array

    Parameters:
    im: nummpy array
        The image to classify

    Returns:
    classe[0] : int
        in [0, 1, 2] corresponding to ['godet-vide', 'pet-clair', 'pet-fonce']
	or 
	in [0, 1, 2, 3] corresponding to ['godet-vide', 'pe-hd-opaque','pet-clair', 'pet-fonce']
	depending on which trained model is used.

   """


    classe = model.predict(im)
    classe =classe.argmax(axis = -1) #taking index of the maximum %
    return classe[0]





def main():

    HEIGHT = 224
    WIDTH = 224

    model = load_model('vgg16_v3.h5')

    im_path = './dataset/wsEN4iv2SliFUuYNXIM-5Q_0b9FT9bgTKSFE4NaMtMCwA_320x200.png'

    img = image.load_img(im_path, target_size=(HEIGHT, WIDTH)) #resize
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)# correct shape for classification

    print(classify(img,model))


main()
