import os


import torch
from PIL import Image

from dotenv import load_dotenv
from image_transforms import get_transform


load_dotenv()

EVAL_MODEL = os.getenv('EVAL_MODEL')
TRANSFORM = get_transform('classification')


def image_grid(imgs, rows, cols):
    assert len(imgs) == rows*cols

    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols*w, rows*h))
    grid_w, grid_h = grid.size

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols*w, i//cols*h))
    return grid


class ModelOperator():
    def __init__(self):
        self.model = torch.load(EVAL_MODEL, map_location='cpu')
        self.model.eval()

    def classify(self, img_path: str) -> int:
        img = Image.open(img_path)
        img_1 = img.crop((img.width // 5, img.height // 5, img.width // 5 * 4, img.height // 5 * 4))
        image_grid([img, img_1], 1, 2).save('a.jpg')
        img_transformed = TRANSFORM(img_1)

        output = self.model(img_transformed.unsqueeze(0))
        print(output)

        # getting all confidence values in an array
        confs = torch.nn.functional.softmax(output, dim=1)
        print(confs)

        print(f'Confidence: {max(confs[0])}')
        # applying confidence threshold to filter no-exhibit photos
        if max(confs[0]) > 0.7:
            prediction = torch.argmax(output)

            print(f'Predicted class: {prediction}')

            return int(prediction)

        return -1
