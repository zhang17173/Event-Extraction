import numpy as np
import torch
import torch.utils.data as Data
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

num_input = 6
num_examples = 20000

train_data = np.loadtxt("06判决结果预测/pytorch回归/data/train6.csv", delimiter=",")
train_features, train_labels = train_data[:, :-1], train_data[:, -1]
train_features = torch.tensor(train_features, dtype=torch.float)
train_labels = torch.tensor(train_labels, dtype=torch.float)

test_data = np.loadtxt("06判决结果预测/pytorch回归/data/test6.csv", delimiter=",")
test_features, test_labels = test_data[:, :-1], test_data[:, -1]
test_features = torch.tensor(test_features, dtype=torch.float)
test_labels = torch.tensor(test_labels, dtype=torch.float)

batch_size = 20

train_dataset = Data.TensorDataset(train_features, train_labels)
train_data_iter = Data.DataLoader(train_dataset, batch_size, shuffle=True)


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.layer1 = nn.Linear(num_input, 256)
        self.layer2 = nn.Linear(256, 64)
        self.layer3 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.layer1(x)
        x = F.relu(x)
        x = self.layer2(x)
        x = F.relu(x)
        x = self.layer3(x)
        return F.relu(x)


net = Net()
loss = nn.MSELoss()
optimizer = optim.Adam(net.parameters(), lr=0.001)

num_epochs = 10
for epoch in range(1, num_epochs + 1):
    for x, y in train_data_iter:
        output = net(x)
        l = loss(output, y.view(-1, 1))
        optimizer.zero_grad()
        l.backward()
        optimizer.step()
    print('epoch %d, loss: %f' % (epoch, l.item()))


def net_test():
    output = net(test_features)
    l = loss(output, test_labels.view(-1, 1))
    print('test loss: %f' % (l.item()))

    print("\n真实值\t预测值\t误差")
    for pred, label in list(zip(output, test_labels))[:20]:
        print("%.1f\t%.1f\t%.1f" %
              (label.item(), pred.item(), abs(label.item()-pred.item())))


net_test()
