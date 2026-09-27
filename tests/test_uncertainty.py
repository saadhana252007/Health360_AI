import numpy as np

from ai.uncertainty.model import UncertaintyEstimator


print("=" * 60)
print("        HEALTH360 UNCERTAINTY TEST")
print("=" * 60)

estimator = UncertaintyEstimator()


print("\n1. HIGH-CONFIDENCE PREDICTION")
print("-" * 60)

high_confidence = np.array(
    [0.05, 0.90, 0.03, 0.02]
)

result_high = estimator.estimate(
    probabilities=high_confidence,
    modality_completeness=1.0,
    image_quality=1.0
)

print("Result:", result_high)


print("\n2. UNCERTAIN PREDICTION")
print("-" * 60)

uncertain = np.array(
    [0.25, 0.26, 0.24, 0.25]
)

result_uncertain = estimator.estimate(
    probabilities=uncertain,
    modality_completeness=1.0,
    image_quality=1.0
)

print("Result:", result_uncertain)


print("\n3. INCOMPLETE INPUT")
print("-" * 60)

result_incomplete = estimator.estimate(
    probabilities=high_confidence,
    modality_completeness=0.5,
    image_quality=1.0
)

print("Result:", result_incomplete)


print("\n4. LOW IMAGE QUALITY")
print("-" * 60)

result_low_quality = estimator.estimate(
    probabilities=high_confidence,
    modality_completeness=1.0,
    image_quality=0.4
)

print("Result:", result_low_quality)


print("\n5. BASIC ASSERTIONS")
print("-" * 60)

assert result_high["confidence"] > result_uncertain["confidence"]

assert result_uncertain["uncertainty"] > result_high["uncertainty"]

assert result_incomplete["confidence"] < result_high["confidence"]

assert result_low_quality["confidence"] < result_high["confidence"]

assert 0.0 <= result_high["confidence"] <= 1.0
assert 0.0 <= result_high["uncertainty"] <= 1.0

print("Confidence comparison: PASSED")
print("Uncertainty comparison: PASSED")
print("Completeness adjustment: PASSED")
print("Image quality adjustment: PASSED")
print("Range checks: PASSED")


print("\n" + "=" * 60)
print("        UNCERTAINTY MODULE READY")
print("=" * 60)