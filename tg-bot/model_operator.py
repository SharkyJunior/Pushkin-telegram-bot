import os


import torch
from PIL import Image

from dotenv import load_dotenv
from image_transforms import get_transform


load_dotenv()

EVAL_MODEL = os.getenv('EVAL_MODEL')
TRANSFORM = get_transform('classification')


class ModelOperator():
    def __init__(self):
        self.model = torch.load(EVAL_MODEL)
        self.model.eval()

    def classify(self, img_path: str) -> int:
        img = Image.open(img_path)
        img_transformed = TRANSFORM(img)

        output = self.model(img_transformed.unsqueeze(0))
        prediction = torch.argmax(output)
        print(prediction)

        return int(prediction)
