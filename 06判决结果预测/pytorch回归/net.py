from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_dataset(csv_path: Path) -> tuple[torch.Tensor, torch.Tensor]:
    data = np.loadtxt(csv_path, delimiter=",", dtype=np.float32)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    features = torch.tensor(data[:, :-1], dtype=torch.float32)
    labels = torch.tensor(data[:, -1], dtype=torch.float32).view(-1, 1)
    return features, labels


class Net(nn.Module):
    def __init__(self, num_input: int = 6) -> None:
        super().__init__()
        self.layer1 = nn.Linear(num_input, 256)
        self.layer2 = nn.Linear(256, 64)
        self.layer3 = nn.Linear(64, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return F.relu(self.layer3(x))


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"

    parser = argparse.ArgumentParser(description="训练回归模型。")
    parser.add_argument("--train", default=str(data_dir / "train6.csv"), help="训练集 CSV。")
    parser.add_argument("--test", default=str(data_dir / "test6.csv"), help="测试集 CSV。")
    parser.add_argument("--epochs", type=int, default=20, help="训练轮数。")
    parser.add_argument("--batch-size", type=int, default=20, help="批大小。")
    parser.add_argument("--lr", type=float, default=1e-3, help="学习率。")
    parser.add_argument("--seed", type=int, default=42, help="随机种子。")
    args = parser.parse_args()

    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_features, train_labels = load_dataset(Path(args.train).resolve())
    test_features, test_labels = load_dataset(Path(args.test).resolve())
    train_loader = DataLoader(TensorDataset(train_features, train_labels), batch_size=args.batch_size, shuffle=True)

    model = Net().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss = 0.0
        for x, y in train_loader:
            x = x.to(device)
            y = y.to(device)
            pred = model(x)
            loss = criterion(pred, y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * len(y)
        print(f"epoch {epoch}: loss={running_loss / max(len(train_loader.dataset), 1):.6f}")

    model.eval()
    with torch.no_grad():
        pred = model(test_features.to(device)).cpu()
        loss = criterion(pred, test_labels).item()
    print(f"test loss: {loss:.6f}")
    print("\n真实值\t预测值\t误差")
    for true_value, pred_value in list(zip(test_labels.squeeze(1).tolist(), pred.squeeze(1).tolist()))[:20]:
        print(f"{true_value:.1f}\t{pred_value:.1f}\t{abs(true_value - pred_value):.1f}")


if __name__ == "__main__":
    main()
