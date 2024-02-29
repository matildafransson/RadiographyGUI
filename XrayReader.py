from PIL import Image
import numpy as np
import glob

class XrayReader():
    def __init__(self,pathXray,skip):
        self.pathXray = pathXray
        self.skip = skip

    def readOneImage(self, path):
        image = np.array(Image.open(path))
        return image

    def readAllImages(self):
        listPathImages = glob.glob(self.pathXray + '/*.tif' )
        listPathImages.sort()



        index = 0
        for i, pathIm in enumerate(listPathImages):

            if i == 0:
                im = self.readOneImage(pathIm)
                vol = np.zeros((int(len(listPathImages) / self.skip), im.shape[0], im.shape[1]))

            if ((i+1) % self.skip) == 0:
                print(pathIm)
                im = self.readOneImage(pathIm)
                vol[index, :, :] = im
                index += 1
        return vol