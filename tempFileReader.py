import numpy as np
import glob



class tempTxtFileReader():

    def __init__(self, path_txtImage, skip):

        self.path_txtImage = path_txtImage
        self.skip = skip

    def readSeqImage(self):

        listPathImages = glob.glob(self.path_txtImage+'/*.asc')
        listPathImages.sort()
        index = 0
        for i, pathIm in enumerate(listPathImages):
            if i == 0:
                im = self.readOneImage(pathIm)
                vol = np.zeros((int(len(listPathImages) / self.skip), im.shape[0], im.shape[1]))

            if ((i+1)%self.skip) == 0:
                im = self.readOneImage(pathIm)
                print(pathIm)

                vol[index,:,:] = im
                index += 1

        return vol


    def readOneImage(self,path):
        self.listaverageTC = []
        self.listframes = []
        f = open(path)
        lines = f.readlines()
        for i, line in enumerate(lines):
            lines[i] = line.replace(',','.')

        data = lines[17:]
        data_np = np.loadtxt(data)

        return data_np

if __name__ == '__main__':
     reader = tempTxtFileReader('./')
     vol = reader.readSeqImage()

