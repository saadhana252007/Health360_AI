from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "data" / "raw"
SPLIT_DIR = ROOT / "data" / "splits"

METADATA_PATH = RAW_DIR / "metadata.csv"
GROUND_TRUTH_PATH = RAW_DIR / "supplements" / "training_gt.csv"

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

def main():
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)

    metadata = pd.read_csv(METADATA_PATH)
    ground_truth = pd.read_csv(GROUND_TRUTH_PATH)

    clinical = metadata[
        metadata["image_type"] == "clinical: close-up"
    ].copy()

    labels = ground_truth.copy()
    labels["class_index"] = labels[CLASS_NAMES].values.argmax(axis=1)

    clinical = clinical.merge(
        labels[["lesion_id", "class_index"]],
        on="lesion_id",
        how="inner",
        validate="one_to_one"
    )

    clinical["image_path"] = clinical["isic_id"].apply(
        lambda x: str(Path("data") / "raw" / "images" / f"{x}.jpg")
    )

    train_ids, temp_ids = train_test_split(
        clinical["lesion_id"],
        test_size=0.30,
        stratify=clinical["class_index"],
        random_state=42
    )

    temp = clinical[clinical["lesion_id"].isin(temp_ids)]

    val_ids, test_ids = train_test_split(
        temp["lesion_id"],
        test_size=0.50,
        stratify=temp["class_index"],
        random_state=42
    )

    train = clinical[clinical["lesion_id"].isin(train_ids)].copy()
    val = clinical[clinical["lesion_id"].isin(val_ids)].copy()
    test = clinical[clinical["lesion_id"].isin(test_ids)].copy()

    columns = [
        "lesion_id",
        "isic_id",
        "image_path",
        "class_index",
    ]

    train[columns].to_csv(SPLIT_DIR / "train.csv", index=False)
    val[columns].to_csv(SPLIT_DIR / "val.csv", index=False)
    test[columns].to_csv(SPLIT_DIR / "test.csv", index=False)

    print("MILK10k split created")
    print(f"Train: {len(train)}")
    print(f"Validation: {len(val)}")
    print(f"Test: {len(test)}")

    print("\nTrain distribution:")
    print(train["class_index"].value_counts().sort_index())

    print("\nValidation distribution:")
    print(val["class_index"].value_counts().sort_index())

    print("\nTest distribution:")
    print(test["class_index"].value_counts().sort_index())

if __name__ == "__main__":
    main()