
import numpy as np
import torch
import torchvision
import os
from dotenv import load_dotenv
from torchvision import datasets, models, transforms
import torch.utils.data as data
import multiprocessing
from sklearn.metrics import confusion_matrix

load_dotenv()

EVAL_MODEL = os.getenv('EVAL_MODEL')
model = torch.load(EVAL_MODEL, map_location='cpu')
model.eval()


bs = 8
EVAL_DIR = os.getenv('EVAL_DIR')


# Prepare the eval data loader
eval_transform = transforms.Compose([
    transforms.Resize(size=256),
    transforms.CenterCrop(size=224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])])
eval_dataset = datasets.ImageFolder(root=EVAL_DIR, transform=eval_transform)
eval_loader = data.DataLoader(
    eval_dataset, batch_size=bs, shuffle=True, pin_memory=True)
# Enable gpu mode, if cuda available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# Number of classes and dataset-size
num_classes = len(eval_dataset.classes)
dsize = len(eval_dataset)
# Class label names
class_names = ['zh-3269', 'zh-3273', 'zh-3299',
               'zh-3309', 'zh-3335', 'zh-3372', 'zh-3405']
# Initialize the prediction and label lists
predlist = torch.zeros(0, dtype=torch.long, device='cpu')
lbllist = torch.zeros(0, dtype=torch.long, device='cpu')
# Evaluate the model accuracy on the dataset
correct = 0
total = 0
sum_max_conf = 0
with torch.no_grad():
    for images, labels in eval_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)

        # getting array of all confidence values
        confs = torch.nn.functional.softmax(outputs, dim=1)

        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        for conf in confs:
            sum_max_conf += max(conf)
        predlist = torch.cat([predlist, predicted.view(-1).cpu()])
        lbllist = torch.cat([lbllist, labels.view(-1).cpu()])
# Overall accuracy
overall_accuracy = 100 * correct / total
avg_conf = sum_max_conf / total
print('Accuracy of the network on the {:d} test images: {:.2f}%'.format(dsize,
                                                                        overall_accuracy))
print(f'Average confidence: {avg_conf}')
# Confusion matrix
conf_mat = confusion_matrix(lbllist.numpy(), predlist.numpy())
print('Confusion Matrix')
print('-'*16)
print(conf_mat, '\n')
