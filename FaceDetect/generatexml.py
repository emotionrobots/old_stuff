import cv2
import os
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
import numpy as np 
import glob

data = pd.read_csv("./data/val_labels.csv",encoding="utf-8")
imgpath = '/home/raj/Downloads/WIDER-Face/images/test/'
imgdata = data [['filename','width','height','class','xmin','ymin','xmax','ymax']].values

def generateXML(height,width,depth,imgfolder,fname,label,points,path):
    root = ET.Element("annotation")
    folder = ET.SubElement(root,"folder").text = imgfolder
    filename = ET.SubElement(root,"filename").text = str(fname[0])+".jpg"
    path = ET.SubElement(root,"path").text = "./"+str(imgfolder)+"/"+str(fname[0])+".jpg"
    source = ET.SubElement(root,"source")
    database = ET.SubElement(source,"database").text = "Unknown"
    size = ET.SubElement(root,"size")
    width = ET.SubElement(size,"width").text = str(width)
    height = ET.SubElement(size,"height").text = str(height)
    depth = ET.SubElement(size,"depth").text = str(depth)
    segmented = ET.SubElement(root,"segmented").text = str(0)
    obj = ET.SubElement(root,"object")
    name = ET.SubElement(obj,"name").text = label
    pose = ET.SubElement(obj,"pose").text = "Unspecified" 
    truncated = ET.SubElement(obj,"truncated").text = str(0) 
    difficult = ET.SubElement(obj,"difficult").text = str(0)
    bndbox = ET.SubElement(obj,"bndbox")
    xmin = ET.SubElement(bndbox,"xmin").text = str(int(points[0]))
    ymin = ET.SubElement(bndbox,"ymin").text = str(int(points[1]))
    xmax = ET.SubElement(bndbox,"xmax").text = str(int(points[2]))
    ymax = ET.SubElement(bndbox,"ymax").text = str(int(points[3]))

    tree = ET.ElementTree(root)
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")

    my_file = Path(XML_FILE_PATH)
    if my_file.exists():
        root = ET.parse(my_file).getroot()
        obj2 = ET.Element("object")
        name = ET.SubElement(obj2,"name").text = label
        pose = ET.SubElement(obj2,"pose").text = "Unspecified" 
        truncated = ET.SubElement(obj2,"truncated").text = str(0) 
        difficult = ET.SubElement(obj2,"difficult").text = str(0)
        bndbox = ET.SubElement(obj2,"bndbox")
        xmin = ET.SubElement(bndbox,"xmin").text = str(int(points[0]))
        ymin = ET.SubElement(bndbox,"ymin").text = str(int(points[1]))
        xmax = ET.SubElement(bndbox,"xmax").text = str(int(points[2]))
        ymax = ET.SubElement(bndbox,"ymax").text = str(int(points[3]))
        root.insert(8,obj2)

        tree = ET.ElementTree(root)
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml()

        with open(XML_FILE_PATH, "w") as f:
            f.write(xmlstr)

    else:
        with open(XML_FILE_PATH, "w") as f:
            f.write(xmlstr)

def prettyPrintXML(XML_FILE_PATH):
    ppfile = Path(XML_FILE_PATH)
    if ppfile.exists():
        x = minidom.parse(XML_FILE_PATH)
        pretty_xml = x.toprettyxml(newl='')
        pretty_xml = os.linesep.join([s for s in pretty_xml.splitlines() if s.strip()])
        with open(XML_FILE_PATH,"w") as f:
            f.write(pretty_xml)


for k in imgdata:
    imgfile = k[0]
    fname = imgfile.split('.jpg')
    imgfolder = 'images'
    label = 'face'
    
    XML_FILE_PATH = imgpath+fname[0]+".xml"
    # print(XML_FILE_PATH)
    img = cv2.imread(imgpath+k[0])
    print(imgpath+k[0])
    xmin = k[4]
    ymin = k[5]
    xmax = k[6]
    ymax = k[7]
    points = (xmin,ymin,xmax,ymax)
    height = k[2]
    width = k[1]
    depth = img.shape[2]
    generateXML(height,width,depth,imgfolder,fname,label,points,XML_FILE_PATH)
    prettyPrintXML(XML_FILE_PATH)
    # img = cv2.rectangle(img,(int(xmin),int(ymin)),(int(xmax),int(ymax)),(0,255,0))
    # cv2.imshow("temp",img)
    # cv2.waitKey()