import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import optim
from torch.autograd import Variable
from torch.utils.data import DataLoader
from torch.utils.data import Dataset
import csv
import os

num_classes = 5
input_size = 6
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class MyDataset(Dataset):
    def __init__(self, csv_file):
        self.df = np.loadtxt(csv_file, delimiter=',', dtype=np.float32)
        self.x_data = torch.Tensor(self.df[:, :-1])
        self.y_data = torch.LongTensor(self.df[:, -1])

    def __len__(self):
        return self.df.shape[0]

    def __getitem__(self, idx):
        return self.x_data[idx], self.y_data[idx]


train_set = MyDataset("data/train6.csv")
train_data = DataLoader(dataset=train_set, batch_size=32, shuffle=True)
test_set = MyDataset("data/test6.csv")
test_data = DataLoader(dataset=test_set, batch_size=32, shuffle=False)


class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        self.layer1 = nn.Linear(input_size, 64)
        self.layer2 = nn.Linear(64, 128)
        self.layer3 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.layer1(x)
        x = F.relu(x)
        x = self.layer2(x)
        x = F.relu(x)
        return self.layer3(x)


net = Net().to(DEVICE)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters(), lr=0.00001)


def train(epoch):
    for batch_idx, (data, target) in enumerate(train_data):
        data, target = Variable(data).to(DEVICE), Variable(target).to(DEVICE)
        optimizer.zero_grad()
        output = net(data)

        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        if (batch_idx + 1) % 200 == 0:
            print("Train Epoch: {} Loss: {:.6f}".format(epoch, loss.item()))


def final_test():
    test_loss = 0

    correct = list(0 for i in range(num_classes))
    total = list(0 for i in range(num_classes))

    if os.path.exists("result.csv"):
        os.remove("result.csv")

    for pattern, target in test_data:
        pattern, target = Variable(pattern).to(DEVICE), Variable(target).to(DEVICE)
        output = net(pattern)
        test_loss += criterion(output, target).item()

        prediction = torch.argmax(output, 1)

        zipped = zip(pattern.data.tolist(), target.data.tolist(), prediction.tolist())
        with open("result.csv", "a") as f:
            f_csv = csv.writer(f)
            f_csv.writerows(zipped)

        res = (prediction == target).squeeze()
        for i in range(len(target)):
            label = target[i]
            correct[label] += res[i].item()
            total[label] += 1
    for i in range(num_classes):
        print("accu of {} :{}".format(i, correct[i] / total[i]))
        print("num of {} : {}".format(i, total[i]))
    print(sum(correct) / sum(total))


for epoch in range(1, 201):
    train(epoch)
final_test()
