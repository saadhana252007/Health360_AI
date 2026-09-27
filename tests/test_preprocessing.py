import numpy as np
import torch

from ai.common.image_quality import ImageQualityChecker
from ai.common.preprocessing import (
    get_training_transform,
    get_validation_transform,
    get_inference_transform,
    preprocess_image,
)


def main():
    print("=" * 60)
    print("        HEALTH360 IMAGE PREPROCESSING TEST")
    print("=" * 60)

    # Create a synthetic RGB-like image for testing.
    # This is ONLY an engineering test image,
    # not a medical image.
    image = np.random.randint(
        0,
        256,
        size=(512, 512, 3),
        dtype=np.uint8
    )

    print("\n1. IMAGE QUALITY CHECK")
    print("-" * 60)

    checker = ImageQualityChecker()

    result = checker.check(image)

    print("Acceptable:", result.is_acceptable)
    print("Width:", result.width)
    print("Height:", result.height)
    print("Blur score:", result.blur_score)
    print("Brightness:", result.brightness_score)
    print("Reasons:", result.reasons)

    print("\n2. TRAINING PREPROCESSING")
    print("-" * 60)

    training_transform = get_training_transform()

    training_tensor = preprocess_image(
        image,
        training_transform
    )

    print("Training tensor shape:", training_tensor.shape)
    print("Training tensor dtype:", training_tensor.dtype)

    print("\n3. VALIDATION PREPROCESSING")
    print("-" * 60)

    validation_transform = get_validation_transform()

    validation_tensor = preprocess_image(
        image,
        validation_transform
    )

    print("Validation tensor shape:", validation_tensor.shape)
    print("Validation tensor dtype:", validation_tensor.dtype)

    print("\n4. INFERENCE PREPROCESSING")
    print("-" * 60)

    inference_transform = get_inference_transform()

    inference_tensor = preprocess_image(
        image,
        inference_transform
    )

    print("Inference tensor shape:", inference_tensor.shape)
    print("Inference tensor dtype:", inference_tensor.dtype)

    print("\n5. BASIC ASSERTIONS")
    print("-" * 60)

    expected_shape = (1, 3, 224, 224)

    assert training_tensor.shape == expected_shape
    assert validation_tensor.shape == expected_shape
    assert inference_tensor.shape == expected_shape

    assert training_tensor.dtype == torch.float32
    assert validation_tensor.dtype == torch.float32
    assert inference_tensor.dtype == torch.float32

    print("All shape checks: PASSED")
    print("All dtype checks: PASSED")

    print("\n" + "=" * 60)
    print("     IMAGE PREPROCESSING READY")
    print("=" * 60)


if __name__ == "__main__":
    main()