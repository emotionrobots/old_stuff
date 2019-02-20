import os
import glob
from shutil import copy2
from pathlib import Path
PATH = '/home/raj/Downloads/WIDER-Face/'


## Copying files from one place to another
def copyfilesinsideFolders(PATH):
    for i in glob.glob(PATH+"*"):
        for j in glob.glob(i+"/*.jpg"):
            if (os.path.isfile(j)):
                copy2(j,PATH)
                print(j)
    return "Done!"

def copyfiles(PATH):
    for i in glob.glob(PATH+"images/test/*.xml"):
        if(os.path.isfile(i)):
            copy2(i,PATH+"images_bw/test/")
    print("Done!")


## Deleting the files which doesnt have xml
def deleteimages(PATH):
    count = 0
    for i in glob.glob(PATH+"*.jpg"):
        xml = i[:-3]
        xml = xml+"xml"
        myfile = Path(xml)
        if myfile.is_file():
            continue
        else:
            count += 1
            print(i)
            os.unlink(i)
    print(count)
    return "Done!"

    
copyfiles(PATH)