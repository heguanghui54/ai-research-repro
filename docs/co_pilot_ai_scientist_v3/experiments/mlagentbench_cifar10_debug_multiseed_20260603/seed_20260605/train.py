import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

SEED = 20260605
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

train_transform = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
])
test_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
])

class SmallBNNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(inplace=True),
            nn.MaxPool2d(2), nn.Dropout(0.10),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(inplace=True),
            nn.MaxPool2d(2), nn.Dropout(0.15),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Linear(128, 10)

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        return self.classifier(x)

def accuracy(model, dataloader, device):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            logits = model(inputs)
            correct += (logits.argmax(dim=1) == labels).sum().item()
            total += labels.numel()
    return 100.0 * correct / max(total, 1)

start = time.time()
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
train_full = datasets.CIFAR10(root="./data", train=True, download=True, transform=train_transform)
train_eval = datasets.CIFAR10(root="./data", train=True, download=True, transform=test_transform)
test_dataset = datasets.CIFAR10(root="./data", train=False, download=True, transform=test_transform)

train_loader = DataLoader(train_full, batch_size=128, shuffle=True, num_workers=2)
train_eval_loader = DataLoader(train_eval, batch_size=256, shuffle=False, num_workers=2)
test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False, num_workers=2)

model = SmallBNNet().to(device)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=8)
criterion = nn.CrossEntropyLoss(label_smoothing=0.05)

for epoch in range(8):
    model.train()
    running = 0.0
    for inputs, labels in train_loader:
        inputs = inputs.to(device)
        labels = labels.to(device)
        optimizer.zero_grad(set_to_none=True)
        loss = criterion(model(inputs), labels)
        loss.backward()
        optimizer.step()
        running += loss.item()
    scheduler.step()
    train_acc = accuracy(model, train_eval_loader, device)
    test_acc = accuracy(model, test_loader, device)
    print(f"Epoch [{epoch+1}/8], loss: {running / len(train_loader):.4f}, Train Accuracy: {train_acc:.2f}%, Test Accuracy: {test_acc:.2f}%")

submission = pd.DataFrame(columns=list(range(10)), index=range(len(test_dataset)))
model.eval()
with torch.no_grad():
    for idx, (inputs, _) in enumerate(test_dataset):
        logits = model(inputs.unsqueeze(0).to(device))
        probs = torch.softmax(logits[0], dim=0).cpu().numpy()
        submission.loc[idx] = probs.tolist()
submission.to_csv("submission.csv")
print(f"Done in {time.time()-start:.2f}s")
