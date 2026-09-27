import sys

import torch
import torchvision
import timm
import cv2
import numpy as np
import pandas as pd
import sklearn
import xgboost
import albumentations as A
import segmentation_models_pytorch as smp
import fastapi
import onnx
import onnxruntime


def main():
    print("=" * 60)
    print("        HEALTH360 AI ENVIRONMENT CHECK")
    print("=" * 60)

    print("\nPYTHON")
    print("-" * 60)
    print("Python:", sys.version)

    print("\nDEEP LEARNING")
    print("-" * 60)
    print("PyTorch:", torch.__version__)
    print("Torchvision:", torchvision.__version__)
    print("CUDA available:", torch.cuda.is_available())

    print("\nDATA / IMAGE PROCESSING")
    print("-" * 60)
    print("NumPy:", np.__version__)
    print("Pandas:", pd.__version__)
    print("OpenCV:", cv2.__version__)
    print("Albumentations:", A.__version__)

    print("\nMACHINE LEARNING")
    print("-" * 60)
    print("Scikit-learn:", sklearn.__version__)
    print("XGBoost:", xgboost.__version__)

    print("\nVISION MODELS")
    print("-" * 60)
    print("timm:", timm.__version__)
    print("Segmentation Models PyTorch:", smp.__version__)

    print("\nBACKEND / DEPLOYMENT")
    print("-" * 60)
    print("FastAPI:", fastapi.__version__)
    print("ONNX:", onnx.__version__)
    print("ONNX Runtime:", onnxruntime.__version__)

    print("\nMODEL CREATION TEST")
    print("-" * 60)

    # Our selected primary skin architecture
    model = timm.create_model(
        "tf_efficientnetv2_s",
        pretrained=False,
        num_classes=11
    )

    print("EfficientNetV2-S: CREATED SUCCESSFULLY")

    # Test an actual forward pass
    x = torch.randn(1, 3, 224, 224)

    with torch.no_grad():
        output = model(x)

    print("Input shape:", x.shape)
    print("Output shape:", output.shape)

    print("\nSEGMENTATION MODEL TEST")
    print("-" * 60)

    # Our planned wound architecture
    wound_model = smp.Unet(
        encoder_name="efficientnet-b3",
        encoder_weights=None,
        in_channels=3,
        classes=1
    )

    print("U-Net + EfficientNet-B3: CREATED SUCCESSFULLY")

    wound_output = wound_model(x)

    print("Wound input shape:", x.shape)
    print("Wound output shape:", wound_output.shape)

    print("\n" + "=" * 60)
    print("       HEALTH360 AI ENVIRONMENT READY")
    print("=" * 60)


if __name__ == "__main__":
    main()