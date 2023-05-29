from torchvision import transforms

interpolation_mode = transforms.InterpolationMode.BILINEAR

image_transforms = {
    'training': transforms.Compose([
        transforms.RandomResizedCrop(size=256, scale=(0.8, 1.0)),
        transforms.RandomRotation(degrees=20),
        transforms.RandomHorizontalFlip(),
        transforms.CenterCrop(size=224),
        transforms.RandomPosterize(5),
        transforms.RandomAutocontrast(0.5),
        transforms.RandomEqualize(),
        transforms.RandomPerspective(distortion_scale=0.4, p=0.5,
                                     interpolation=interpolation_mode,
                                     fill=128),
    ]
    ),
    'validation': transforms.Compose([
        transforms.Resize(size=256),
        transforms.CenterCrop(size=224),
        transforms.RandomRotation(degrees=10),
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


def get_transform(type: str) -> transforms.Compose:
    """Returns composed transform of a PIL image

    :param type: transform type
    :type type: str
    :return: selected transform
    :rtype: transforms.Compose
    """
    return image_transforms[type]
