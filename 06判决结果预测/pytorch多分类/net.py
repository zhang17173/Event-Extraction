from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import optim
from torch.utils.data import DataLoader
from torch.utils.data import Dataset

NUM_CLASSES = 5
INPUT_SIZE = 6


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class CsvDataset(Dataset):
    def __init__(self, csv_file: Path):
        data = np.loadtxt(csv_file, delimiter=",", dtype=np.float32)
        if data.ndim == 1:
            data = data.reshape(1, -1)
        self.x_data = torch.tensor(data[:, :-1], dtype=torch.float32)
        self.y_data = torch.tensor(data[:, -1], dtype=torch.long)

    def __len__(self) -> int:
        return self.x_data.shape[0]

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.x_data[idx], self.y_data[idx]


class Net(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.layer1 = nn.Linear(INPUT_SIZE, 64)
        self.layer2 = nn.Linear(64, 128)
        self.layer3 = nn.Linear(128, NUM_CLASSES)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        return self.layer3(x)


def train(model: Net, loader: DataLoader, criterion: nn.Module, optimizer: optim.Optimizer, device: torch.device) -> float:
    model.train()
    total_loss = 0.0
    for data, target in loader:
        data = data.to(device)
        target = target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(target)
    return total_loss / max(len(loader.dataset), 1)


def evaluate(model: Net, loader: DataLoader, criterion: nn.Module, device: torch.device, result_file: Path) -> float:
    model.eval()
    total_loss = 0.0
    correct = [0] * NUM_CLASSES
    total = [0] * NUM_CLASSES

    with result_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        with torch.no_grad():
            for pattern, target in loader:
                pattern = pattern.to(device)
                target = target.to(device)
                output = model(pattern)
                total_loss += criterion(output, target).item() * len(target)

                prediction = torch.argmax(output, dim=1)
                pattern_rows = pattern.cpu().tolist()
                target_rows = target.cpu().tolist()
                prediction_rows = prediction.cpu().tolist()
                writer.writerows([features + [true_label, pred_label] for features, true_label, pred_label in zip(pattern_rows, target_rows, prediction_rows)])

                for true_label, pred_label in zip(target_rows, prediction_rows):
                    total[true_label] += 1
                    if true_label == pred_label:
                        correct[true_label] += 1

    for label in range(NUM_CLASSES):
        accuracy = correct[label] / total[label] if total[label] else 0.0
        print(f"class {label}: 样本数={total[label]}, 准确率={accuracy:.4f}")
    overall = sum(correct) / max(sum(total), 1)
    print(f"总体准确率: {overall:.4f}")
    return total_loss / max(len(loader.dataset), 1)


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "data"

    parser = argparse.ArgumentParser(description="训练多分类判决结果模型。")
    parser.add_argument("--train", default=str(data_dir / "train6.csv"), help="训练集 CSV。")
    parser.add_argument("--test", default=str(data_dir / "test6.csv"), help="测试集 CSV。")
    parser.add_argument("--epochs", type=int, default=50, help="训练轮数。")
    parser.add_argument("--batch-size", type=int, default=32, help="批大小。")
    parser.add_argument("--lr", type=float, default=1e-4, help="学习率。")
    parser.add_argument("--seed", type=int, default=42, help="随机种子。")
    parser.add_argument("--result", default=str(script_dir / "result.csv"), help="测试结果输出。")
    args = parser.parse_args()

    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_set = CsvDataset(Path(args.train).resolve())
    test_set = CsvDataset(Path(args.test).resolve())
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_set, batch_size=args.batch_size, shuffle=False)

    model = Net().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    for epoch in range(1, args.epochs + 1):
        train_loss = train(model, train_loader, criterion, optimizer, device)
        if epoch == 1 or epoch % 10 == 0 or epoch == args.epochs:
            print(f"epoch {epoch}: train_loss={train_loss:.6f}")

    test_loss = evaluate(model, test_loader, criterion, device, Path(args.result).resolve())
    print(f"test_loss={test_loss:.6f}")


if __name__ == "__main__":
    main()
