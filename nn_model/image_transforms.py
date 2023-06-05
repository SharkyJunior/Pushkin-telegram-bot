import random

import torchvision.transforms.v2 as transforms
import torchvision

torchvision.disable_beta_transforms_warning()

interpolation_mode = transforms.InterpolationMode.BILINEAR


def get_image_transform(type: str):
    image_transforms = {
        'training': transforms.Compose([
            transforms.CenterCrop(size=random.randint(600, 900)),
            transforms.RandomResizedCrop(size=256),
            transforms.RandomPerspective(distortion_scale=random.uniform(0.3, 0.7), p=1,
                                         interpolation=interpolation_mode,
                                         fill=random.randint(64, 224)),
            transforms.RandomRotation(degrees=random.randint(5, 60)),
            transforms.RandomHorizontalFlip(),
            # transforms.RandomPosterize(5),
            # transforms.RandomAutocontrast(0.5),
            transforms.RandomEqualize(),
            transforms.ColorJitter(),
        ]
        ),
        'validation': transforms.Compose([
            transforms.CenterCrop(size=random.randint(100, 400)),
            transforms.Resize(size=256),
            transforms.RandomRotation(degrees=(5, 20)),
            transforms.RandomPerspective(distortion_scale=random.uniform(0.1, 0.3), p=1,
                                         interpolation=interpolation_mode,
                                         fill=random.randint(0, 256)),
        ]
        ),
        'classification': transforms.Compose([
            transforms.Resize(size=256),
            transforms.CenterCrop(size=224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ]
        ),
    }

    return image_transforms[type]


def get_transform(type: str) -> transforms.Compose:
    """Returns composed transform of a PIL image

    :param type: transform type
    :type type: str
    :return: selected transform
    :rtype: transforms.Compose
    """
    return image_transforms[type]
