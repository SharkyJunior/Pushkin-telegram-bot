import os
from image_transforms import get_transform
from dotenv import load_dotenv
from PIL import Image

load_dotenv()


def progress_bar(current, total, bar_length=20):
    fraction = current / total

    arrow = int(fraction * bar_length) * '#'
    padding = int(bar_length - len(arrow)) * ' '

    return f'[{arrow}{padding}] {int(fraction*100)}%'


dataset_path = os.getenv('DATASET_PATH')
init_image_path = os.getenv('INITIAL_IMAGE_PATH')

dest_dir_name = 'training'


names = ['zh-2369', 'zh-3273', 'zh-3335', 'zh-3372', 'zh-3405']
# names = ['zh-3299', 'zh-3309']
n = 500

try:
    os.mkdir(os.path.join(dataset_path, dest_dir_name))
except Exception:
    pass

for i in range(len(names)):
    img_a = Image.open((os.getenv('INITIAL_IMAGE_PATH'),
                        f"{names[i]}-0.jpg"))

    try:
        os.mkdir(os.path.join(dataset_path, dest_dir_name, names[i]))
    except Exception:
        pass

    for x in range(n):
        img_b = get_transform(dest_dir_name)(img_a)
        img_b.save(f'dataset/{dest_dir_name}/{names[i]}/{x}.jpg')
        print(
            f'{names[i]} ({i+1}/{len(names)}): {progress_bar(x+1, n)}',
            end='\r')

    print()
