import os
from image_transforms import get_image_transform
from dotenv import load_dotenv
from PIL import Image
from utilities import progress_bar

load_dotenv()


dataset_path = os.getenv('DATASET_PATH')
init_image_path = os.getenv('INITIAL_IMAGE_PATH')

dest_dir_name = 'training'


names = ['zh-3269', 'zh-3273', 'zh-3299',
         'zh-3309', 'zh-3335', 'zh-3372', 'zh-3405']
n = 500

try:
    os.mkdir(os.path.join(dataset_path, dest_dir_name))
except Exception:
    pass

for i in range(len(names)):
    img_a = Image.open(os.getenv('INITIAL_IMAGE_PATH') + f"{names[i]}-0.jpg")

    try:
        os.mkdir(os.path.join(dataset_path, dest_dir_name, names[i]))
    except Exception:
        pass

    for x in range(n):
        img_b = get_image_transform(dest_dir_name)(img_a)
        img_b.save(f'dataset/{dest_dir_name}/{names[i]}/{x}.jpg')
        print(
            f'{names[i]} ({i+1}/{len(names)}): {progress_bar(x+1, n)}',
            end='\r')

    print()
