from pathlib import Path
import random

import numpy as np
import pandas as pd
import timm
import torch
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
BATCH_SIZE = 16
HEAD_EPOCHS = 20
LEARNING_RATE = 1e-3
SEED = 42

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

class SkinDataset(Dataset):
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)
        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        row = self.data.iloc[index]
        image_path = ROOT / row["image_path"]
        image = Image.open(image_path).convert("RGB")
        image = self.transform(image)
        label = int(row["class_index"])
        return image, label

def extract_features(model, loader, device):
    features = []
    labels = []

    model.eval()

    with torch.no_grad():
        for images, batch_labels in loader:
            images = images.to(device)

            output = model.forward_features(images)
            output = model.global_pool(output)
            output = output.flatten(1)

            features.append(output.cpu())
            labels.append(batch_labels)

    return torch.cat(features), torch.cat(labels)

def evaluate_head(head, features, labels):
    head.eval()

    with torch.no_grad():
        logits = head(features)
        predictions = logits.argmax(dim=1).numpy()

    targets = labels.numpy()

    accuracy = accuracy_score(targets, predictions)

    macro_f1 = f1_score(
        targets,
        predictions,
        average="macro",
        zero_division=0
    )

    return accuracy, macro_f1, targets, predictions

def main():
    set_seed(SEED)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    device = torch.device("cpu")

    train_dataset = SkinDataset(SPLIT_DIR / "train.csv")
    val_dataset = SkinDataset(SPLIT_DIR / "val.csv")
    test_dataset = SkinDataset(SPLIT_DIR / "test.csv")

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    print("Loading pretrained EfficientNetV2-S")

    backbone = timm.create_model(
        "tf_efficientnetv2_s",
        pretrained=True,
        num_classes=NUM_CLASSES
    )

    backbone = backbone.to(device)

    for parameter in backbone.parameters():
        parameter.requires_grad = False

    print("Extracting training features")

    train_features, train_labels = extract_features(
        backbone,
        train_loader,
        device
    )

    print("Extracting validation features")

    val_features, val_labels = extract_features(
        backbone,
        val_loader,
        device
    )

    print("Extracting test features")

    test_features, test_labels = extract_features(
        backbone,
        test_loader,
        device
    )

    feature_dim = train_features.shape[1]

    print(f"Feature dimension: {feature_dim}")
    print(f"Training samples: {len(train_features)}")
    print(f"Validation samples: {len(val_features)}")
    print(f"Test samples: {len(test_features)}")

    counts = torch.bincount(
        train_labels,
        minlength=NUM_CLASSES
    ).float()

    weights = len(train_labels) / (
        NUM_CLASSES * counts.clamp_min(1)
    )

    head = nn.Linear(
        feature_dim,
        NUM_CLASSES
    )

    criterion = nn.CrossEntropyLoss(
        weight=weights
    )

    optimizer = torch.optim.AdamW(
        head.parameters(),
        lr=LEARNING_RATE
    )

    best_macro_f1 = -1.0

    for epoch in range(HEAD_EPOCHS):
        head.train()

        optimizer.zero_grad()

        logits = head(train_features)

        loss = criterion(
            logits,
            train_labels
        )

        loss.backward()

        optimizer.step()

        val_accuracy, val_macro_f1, _, _ = evaluate_head(
            head,
            val_features,
            val_labels
        )

        print(
            f"Epoch {epoch + 1}/{HEAD_EPOCHS} "
            f"Loss={loss.item():.4f} "
            f"ValAcc={val_accuracy:.4f} "
            f"ValMacroF1={val_macro_f1:.4f}"
        )

        if val_macro_f1 > best_macro_f1:
            best_macro_f1 = val_macro_f1

            torch.save(
                {
                    "backbone_state_dict": backbone.state_dict(),
                    "head_state_dict": head.state_dict(),
                    "class_names": CLASS_NAMES,
                    "feature_dim": feature_dim,
                    "image_size": IMAGE_SIZE,
                    "best_val_macro_f1": best_macro_f1
                },
                MODEL_DIR / "best_skin_model.pth"
            )

    checkpoint = torch.load(
        MODEL_DIR / "best_skin_model.pth",
        map_location=device,
        weights_only=False
    )

    head.load_state_dict(
        checkpoint["head_state_dict"]
    )

    test_accuracy, test_macro_f1, targets, predictions = evaluate_head(
        head,
        test_features,
        test_labels
    )

    print("\nFinal Test Results")
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

    print(
        f"\nSaved model: {MODEL_DIR / 'best_skin_model.pth'}"
    )

if __name__ == "__main__":
    main()