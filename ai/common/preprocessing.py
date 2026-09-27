import cv2
import numpy as np
import torch

import albumentations as A
from albumentations.pytorch import ToTensorV2


# ImageNet normalization.
# We use this because our primary vision models use
# pretrained ImageNet weights.
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


IMAGE_SIZE = 224


def get_training_transform(image_size: int = IMAGE_SIZE):
    """
    Training preprocessing.

    Includes augmentation because the model should learn
    to handle realistic variations in user images.
    """

    return A.Compose([
        A.Resize(
            height=image_size,
            width=image_size
        ),

        A.HorizontalFlip(
            p=0.5
        ),

        A.Affine(
            scale=(0.9, 1.1),
            translate_percent=(-0.05, 0.05),
            rotate=(-15, 15),
            p=0.5
        ),

        A.RandomBrightnessContrast(
            brightness_limit=0.15,
            contrast_limit=0.15,
            p=0.3
        ),

        A.Normalize(
            mean=IMAGENET_MEAN,
            std=IMAGENET_STD,
            max_pixel_value=255.0
        ),

        ToTensorV2()
    ])


def get_validation_transform(image_size: int = IMAGE_SIZE):
    """
    Validation/test preprocessing.

    No random augmentation is applied.
    """

    return A.Compose([
        A.Resize(
            height=image_size,
            width=image_size
        ),

        A.Normalize(
            mean=IMAGENET_MEAN,
            std=IMAGENET_STD,
            max_pixel_value=255.0
        ),

        ToTensorV2()
    ])


def get_inference_transform(image_size: int = IMAGE_SIZE):
    """
    Production inference preprocessing.

    Deterministic preprocessing for user-uploaded images.
    """

    return A.Compose([
        A.Resize(
            height=image_size,
            width=image_size
        ),

        A.Normalize(
            mean=IMAGENET_MEAN,
            std=IMAGENET_STD,
            max_pixel_value=255.0
        ),

        ToTensorV2()
    ])


def preprocess_image(
    image: np.ndarray,
    transform
) -> torch.Tensor:
    """
    Apply a preprocessing transform to an OpenCV image.

    OpenCV gives us BGR images, while most deep-learning
    pipelines expect RGB images.
    """

    if image is None:
        raise ValueError("Image cannot be None.")

    # BGR → RGB
    image_rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    transformed = transform(image=image_rgb)

    tensor = transformed["image"]

    # Ensure batch dimension exists.
    if tensor.ndim == 3:
        tensor = tensor.unsqueeze(0)

    return tensor.float()