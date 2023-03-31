import os

import cv2
import numpy as np
from dotenv import load_dotenv

from PIL import Image
import numpy as np


load_dotenv()


def noisy(noise_type, image):
    if noise_type == "gauss":
        row, col, ch = image.shape
        mean = 0
        var = 0.1
        sigma = var**0.5
        gauss = np.random.normal(mean, sigma, (row, col, ch))
        gauss = gauss.reshape(row, col, ch)
        noisy = image + gauss
        return noisy

    elif noise_type == "s&p":
        row, col, ch = image.shape
        s_vs_p = 0.5
        amount = 0.004
        out = np.copy(image)
        # Salt mode
        num_salt = np.ceil(amount * image.size * s_vs_p)
        coords = [np.random.randint(0, i - 1, int(num_salt))
                  for i in image.shape]
        out[coords] = 1

        # Pepper mode
        num_pepper = np.ceil(amount * image.size * (1. - s_vs_p))
        coords = [np.random.randint(0, i - 1, int(num_pepper))
                  for i in image.shape]
        out[coords] = 0
        return out

    elif noise_type == "poisson":
        vals = len(np.unique(image))
        vals = 2 ** np.ceil(np.log2(vals))
        noisy = np.random.poisson(image * vals) / float(vals)
        return noisy

    elif noise_type == "speckle":
        row, col, ch = image.shape
        gauss = np.random.randn(row, col, ch)
        gauss = gauss.reshape(row, col, ch)
        noisy = image + image * gauss
        return noisy


def load_image(infilename):
    img = Image.open(infilename)
    img.load()
    data = np.asarray(img, dtype="int32")
    return data


def save_image(npdata, outfilename):
    img = Image.fromarray(npdata.astype(np.uint8), 'RGB')
    img.save(outfilename)


def main():
    for root, dirs, files in os.walk(os.getenv('DATASET_PATH')):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for name in files:
            pathname = os.path.join(root, name)
            print(pathname)
            img = load_image(pathname)
            # noisy_img = noisy('gauss', img)
            save_image(noisy('gauss', img), pathname + '-noisy.jpg')


main()
