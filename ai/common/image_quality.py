import cv2
import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class ImageQualityResult:
    """
    Result of an image quality assessment.
    """

    is_acceptable: bool
    width: int
    height: int
    blur_score: float
    brightness_score: float
    reasons: List[str]


class ImageQualityChecker:
    """
    Performs basic engineering-level image quality checks.

    These thresholds are initial prototype thresholds.
    They must be tuned using real project datasets later.
    """

    def __init__(
        self,
        min_width: int = 224,
        min_height: int = 224,
        min_blur_score: float = 30.0,
        min_brightness: float = 25.0,
        max_brightness: float = 235.0,
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.min_blur_score = min_blur_score
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness

    def check(self, image: np.ndarray) -> ImageQualityResult:
        """
        Check whether an image has sufficient basic visual quality.
        """

        reasons = []

        if image is None:
            return ImageQualityResult(
                is_acceptable=False,
                width=0,
                height=0,
                blur_score=0.0,
                brightness_score=0.0,
                reasons=["Image could not be loaded."]
            )

        if image.ndim not in (2, 3):
            return ImageQualityResult(
                is_acceptable=False,
                width=0,
                height=0,
                blur_score=0.0,
                brightness_score=0.0,
                reasons=["Unsupported image format."]
            )

        height, width = image.shape[:2]

        # Resolution check
        if width < self.min_width or height < self.min_height:
            reasons.append(
                f"Image resolution is too low. "
                f"Minimum required: {self.min_width}x{self.min_height}."
            )

        # Convert to grayscale for blur and brightness checks
        if image.ndim == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Blur score using variance of Laplacian.
        # Lower value generally means the image is blurrier.
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        if blur_score < self.min_blur_score:
            reasons.append("Image appears too blurry.")

        # Mean brightness
        brightness_score = float(np.mean(gray))

        if brightness_score < self.min_brightness:
            reasons.append("Image appears too dark.")

        if brightness_score > self.max_brightness:
            reasons.append("Image appears too bright.")

        return ImageQualityResult(
            is_acceptable=len(reasons) == 0,
            width=width,
            height=height,
            blur_score=blur_score,
            brightness_score=brightness_score,
            reasons=reasons,
        )


def load_image(image_path: str) -> np.ndarray:
    """
    Load an image from disk using OpenCV.

    OpenCV loads images in BGR format.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    return image