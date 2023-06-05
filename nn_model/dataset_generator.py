import os

from dotenv import load_dotenv
from image_transforms import get_image_transform
from PIL import Image
from utilities import progress_bar

load_dotenv()


dataset_path = os.getenv('DATASET_PATH')
init_image_path = os.getenv('INITIAL_IMAGE_PATH')

dest_dir_name = 'training'


# names = ['zh-3269', 'zh-3273', 'zh-3299',
#          'zh-3309', 'zh-3335', 'zh-3372', 'zh-3405']
n = 300
class_amt = 12

try:
    os.mkdir(os.path.join(dataset_path, dest_dir_name))
except Exception:
    pass

for i in range(class_amt):
    img_a = Image.open(os.getenv('INITIAL_IMAGE_PATH') + f"{i}.jpg")

    try:
        os.mkdir(os.path.join(dataset_path, dest_dir_name, str(i)))
    except Exception:
        pass

    for x in range(n):
        img_b = get_image_transform(dest_dir_name)(img_a)
        img_b.save(f'dataset/{dest_dir_name}/{i}/{x}.jpg')
        print(
            f'{i} ({i+1}/{class_amt}): {progress_bar(x+1, n)}',
            end='\r')

    print()
