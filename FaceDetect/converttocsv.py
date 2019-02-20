import numpy
import cv2
import os
import io
import pandas as pd

xml_list = []
def get_csv(f):
    
    height = None # Image height
    width = None # Image width
    filename = None # Filename of the image. Empty if image is not from file
    encoded_image_data = None # Encoded image bytes
    image_format = b'jpeg' # b'jpeg' or b'png'
    xmins = [] # List of normalized left x coordinates in bounding box (1 per box)
    xmaxs = [] # List of normalized right x coordinates in bounding box (1 per box)
    ymins = [] # List of normalized top y coordinates in bounding box (1 per box)
    ymaxs = [] # List of normalized bottom y coordinates in bounding box (1 per box)
    classes_text = [] # List of string class name of bounding box (1 per box)
    classes = [] # List of integer class id of bounding box (1 per box)

    filename = f.readline().rstrip()
    # print(filename)
    filepath = os.path.join("./WIDER_train/images/", filename)
    # print(filepath)
    image_raw = cv2.imread(filepath)

    height, width, channel = image_raw.shape
    # print("height is %d, width is %d, channel is %d" % (height, width, channel))
    face_num = int(f.readline().rstrip())

    for i in range(face_num):
        annot = f.readline().rstrip().split()
        if (float(annot[2]) > 25.0):
            if (float(annot[3]) > 30.0):
                value = (filename,int(width),int(height),'face',int(annot[0]),int(annot[1]),int(int(annot[0])+int(annot[2])),int(int(annot[1])+int(annot[3])))
                xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df

f = open("./wider_face_split/wider_face_train_bbx_gt.txt")
for image_idx in range(12880):
    print("image idx is %d" % image_idx)
    xml_df = get_csv(f)
    xml_df.to_csv('./data/train_labels.csv',index=None)
print("Done")
