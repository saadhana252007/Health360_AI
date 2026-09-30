from pathlib import Path
import random

import numpy as np
import pandas as pd
import torch
import timm
from PIL import Image
from sklearn.metrics import accuracy_score, f1_score, classification_report
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[3]
SPLIT_DIR = ROOT / "data" / "splits"
MODEL_DIR = ROOT / "models" / "skin"

CLASS_NAMES = [
    "AKIEC",
    "BCC",
    "BEN_OTH",
    "BKL",
    "DF",
    "INF",
    "MAL_OTH",
    "MEL",
    "NV",
    "SCCKA",
    "VASC",
]

NUM_CLASSES = len(CLASS_NAMES)
IMAGE_SIZE = 224
BATCH_SIZE = 8
EPOCHS = 1
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4
SEED = 42
NUM_WORKERS = 0

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

class SkinDataset(Dataset):
    def __init__(self, csv_path, transform):
        self.data = pd.read_csv(csv_path)
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        row = self.data.iloc[index]
        image_path = ROOT / row["image_path"]

        image = Image.open(image_path).convert("RGB")
        image = self.transform(image)

        label = int(row["class_index"])

        return image, label

def build_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(
            brightness=0.2,
            contrast=0.2,
            saturation=0.2
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    eval_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    return train_transform, eval_transform

def create_class_weights(train_df):
    counts = train_df["class_index"].value_counts().sort_index()
    counts = counts.reindex(range(NUM_CLASSES), fill_value=0)

    weights = len(train_df) / (
        NUM_CLASSES * counts.replace(0, np.nan)
    )

    weights = weights.fillna(0.0)

    return torch.tensor(
        weights.values,
        dtype=torch.float32
    )

def evaluate(model, loader, criterion, device):
    model.eval()

    total_loss = 0.0
    predictions = []
    targets = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * images.size(0)

            predictions.extend(
                outputs.argmax(dim=1).cpu().numpy()
            )

            targets.extend(
                labels.cpu().numpy()
            )

    average_loss = total_loss / len(loader.dataset)

    accuracy = accuracy_score(targets, predictions)

    macro_f1 = f1_score(
        targets,
        predictions,
        average="macro",
        zero_division=0
    )

    return average_loss, accuracy, macro_f1, targets, predictions

def main():
    set_seed(SEED)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    device = torch.device("cpu")

    train_csv = SPLIT_DIR / "train.csv"
    val_csv = SPLIT_DIR / "val.csv"
    test_csv = SPLIT_DIR / "test.csv"

    train_df = pd.read_csv(train_csv)

    train_transform, eval_transform = build_transforms()

    train_dataset = SkinDataset(
        train_csv,
        train_transform
    )

    val_dataset = SkinDataset(
        val_csv,
        eval_transform
    )

    test_dataset = SkinDataset(
        test_csv,
        eval_transform
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS
    )

    model = timm.create_model(
        "tf_efficientnetv2_s",
        pretrained=True,
        num_classes=NUM_CLASSES
    )

    model = model.to(device)

    class_weights = create_class_weights(train_df).to(device)

    criterion = nn.CrossEntropyLoss(
        weight=class_weights
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=EPOCHS
    )

    best_macro_f1 = -1.0
    best_epoch = -1

    for epoch in range(EPOCHS):
        model.train()

        running_loss = 0.0

        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            outputs = model(images)

            loss = criterion(
                outputs,
                labels
            )

            loss.backward()

            optimizer.step()

            running_loss += loss.item() * images.size(0)

        scheduler.step()

        train_loss = running_loss / len(train_loader.dataset)

        val_loss, val_accuracy, val_macro_f1, _, _ = evaluate(
            model,
            val_loader,
            criterion,
            device
        )

        print(
            f"Epoch {epoch + 1}/{EPOCHS} "
            f"TrainLoss={train_loss:.4f} "
            f"ValLoss={val_loss:.4f} "
            f"ValAcc={val_accuracy:.4f} "
            f"ValMacroF1={val_macro_f1:.4f}"
        )

        if val_macro_f1 > best_macro_f1:
            best_macro_f1 = val_macro_f1
            best_epoch = epoch + 1

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "class_names": CLASS_NAMES,
                    "image_size": IMAGE_SIZE,
                    "best_val_macro_f1": best_macro_f1,
                    "epoch": best_epoch
                },
                MODEL_DIR / "best_skin_model.pth"
            )

            print(
                f"Saved best model at epoch {best_epoch}"
            )

    checkpoint = torch.load(
        MODEL_DIR / "best_skin_model.pth",
        map_location=device,
        weights_only=False
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    test_loss, test_accuracy, test_macro_f1, targets, predictions = evaluate(
        model,
        test_loader,
        criterion,
        device
    )

    print("\nFinal Test Results")
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Test Accuracy: {test_accuracy:.4f}")
    print(f"Test Macro F1: {test_macro_f1:.4f}")

    print("\nClassification Report")
    print(
        classification_report(
            targets,
            predictions,
            labels=list(range(NUM_CLASSES)),
            target_names=CLASS_NAMES,
            zero_division=0
        )
    )

if __name__ == "__main__":
    main()