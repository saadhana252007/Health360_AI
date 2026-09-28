import numpy as np

from backend.services.ai_service import AIService


def test_ai_service_without_image():
    service = AIService()

    symptoms = {
        "severity": 5,
        "duration_days": 2,
        "frequency": 3,
        "progression": 1,
        "site": "head",
        "character": "dull",
        "trigger": "stress",
        "associated_symptoms": ["fatigue"],
        "pre_symptoms": [],
        "post_symptoms": []
    }

    patient = {
        "age": 18,
        "sex": 0,
        "bmi": 21.5,
        "heart_rate": 78,
        "systolic_bp": 115,
        "diastolic_bp": 75,
        "spo2": 98,
        "temperature": 36.7,
        "diabetes": 0,
        "hypertension": 0,
        "asthma": 0,
        "heart_disease": 0,
        "kidney_disease": 0,
        "liver_disease": 0,
        "thyroid": 0,
        "previous_cancer": 0,
        "family_diabetes": 0,
        "family_heart_disease": 0,
        "family_hypertension": 0,
        "family_cancer": 0,
        "sleep_hours": 7,
        "activity_level": 2,
        "tobacco": 0,
        "alcohol": 0,
        "stress_level": 2
    }

    result = service.analyze(
        symptoms=symptoms,
        patient=patient
    )

    assert "symptom_result" in result
    assert "patient_result" in result
    assert "fusion_result" in result
    assert "uncertainty" in result

    assert np.array(result["fusion_result"]["health_vector"]).shape == (1, 7)
    assert 0.0 <= result["fusion_result"]["confidence"] <= 1.0
    assert 0.0 <= result["fusion_result"]["completeness"] <= 1.0

def create_test_image():
    return np.random.randint(
        0,
        256,
        (512, 512, 3),
        dtype=np.uint8
    )


def test_ai_service_skin_image():
    service = AIService()
    image = create_test_image()

    result = service.analyze(
        image=image,
        image_type="skin",
        symptoms={},
        patient={}
    )

    assert result["image_result"]["type"] == "skin"
    assert "prediction" in result["image_result"]
    assert "embedding" in result["image_result"]

    prediction = np.array(result["image_result"]["prediction"])
    embedding = np.array(result["image_result"]["embedding"])

    assert prediction.shape == (1, 11)
    assert embedding.shape == (1, 1280)


def test_ai_service_oral_image():
    service = AIService()
    image = create_test_image()

    result = service.analyze(
        image=image,
        image_type="oral",
        symptoms={},
        patient={}
    )

    assert result["image_result"]["type"] == "oral"
    assert "prediction" in result["image_result"]
    assert "embedding" in result["image_result"]

    prediction = np.array(result["image_result"]["prediction"])
    embedding = np.array(result["image_result"]["embedding"])

    assert prediction.shape == (1, 4)
    assert embedding.shape == (1, 512)


def test_ai_service_wound_image():
    service = AIService()
    image = create_test_image()

    result = service.analyze(
        image=image,
        image_type="wound",
        symptoms={},
        patient={}
    )

    assert result["image_result"]["type"] == "wound"
    assert "segmentation" in result["image_result"]
    assert "classification" in result["image_result"]
    assert "embedding" in result["image_result"]

    segmentation = np.array(result["image_result"]["segmentation"])
    classification = np.array(result["image_result"]["classification"])
    embedding = np.array(result["image_result"]["embedding"])

    assert segmentation.shape == (1, 1, 224, 224)
    assert classification.shape == (1, 8)
    assert embedding.shape == (1, 384)

def test_ai_service_invalid_image_type():
    service = AIService()
    image = create_test_image()

    try:
        service.analyze(
            image=image,
            image_type="xray",
            symptoms={},
            patient={}
        )
        assert False
    except ValueError as error:
        assert str(error) == "Unsupported image type: xray"    