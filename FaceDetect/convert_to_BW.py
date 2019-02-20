import cv2  
import numpy as np
from glob import glob


def load_image_into_numpy_array(image):
    # The function supports only grayscale images
    last_axis = -1
    dim_to_repeat = 2
    repeats = 3
    grscale_img_3dims = np.expand_dims(image, last_axis)
    training_image = np.repeat(grscale_img_3dims, repeats, dim_to_repeat).astype('uint8')
    assert len(training_image.shape) == 3
    assert training_image.shape[-1] == 3
    return training_image

PATH = "/home/raj/Downloads/WIDER-Face/images/train/"

for i in glob(PATH+"*.jpg"):
    filename = i.split('.')
    imgname = filename[0].split('/')
    img = cv2.imread(i,0)
    img = load_image_into_numpy_array(img)
    cv2.imwrite("/home/raj/Downloads/WIDER-Face/images_bw/train/"+imgname[7]+".jpg",img)
    
print("Done!")