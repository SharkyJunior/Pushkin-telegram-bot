import random
import torchvision.transforms as transforms

import torch
from PIL import Image

img_a = Image.open(
    "/Users/sharkyjunior/Documents/Pushkin-telegram-bot/nn_model/zh3405-0.jpg")


image_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(size=512, scale=(0.8, 1.0)),
        transforms.RandomRotation(degrees=20),
        transforms.RandomHorizontalFlip(),
        transforms.CenterCrop(size=448),
        transforms.RandomPosterize(5),
        transforms.RandomAutocontrast(0.5),
        transforms.RandomEqualize(),
        transforms.RandomPerspective(distortion_scale=0.4, p=0.5,
                                     interpolation=transforms.InterpolationMode.BILINEAR, fill=128),
        # transforms.ToTensor(),
        # transforms.Normalize([0.485, 0.456, 0.406],
        #                   [0.229, 0.224, 0.225])
    ]),
    'valid': transforms.Compose([
        transforms.Resize(size=256),
        transforms.CenterCrop(size=224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
}

transform = transforms.RandomOrder([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(30),
    transforms.RandomAffine(30),
    transforms.RandomPerspective(distortion_scale=0.5, p=0.5,
                                 interpolation=transforms.InterpolationMode.BILINEAR, fill=0),
    transforms.RandomCrop(800),
    transforms.RandomPosterize((5, 7)),
    transforms.RandomAdjustSharpness(5),
    transforms.RandomAutocontrast(),
    transforms.RandomEqualize()
])

n = 500
name = 'zh-3405'
for i in range(n):
    img_b = image_transforms['train'](img_a)
    img_b.save(f'dataset/{name}/{name}-{i}.jpg')
    print(f'{i+1}/{n} done')
