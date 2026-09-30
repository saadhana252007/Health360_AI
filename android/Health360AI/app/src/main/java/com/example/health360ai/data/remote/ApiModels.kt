package com.example.health360ai.data.remote

import com.google.gson.annotations.SerializedName

data class CheckupRequest(
    val user_id: String,
    val symptoms: Map<String, Any>,
    val patient: Map<String, Any>
)

data class CheckupResponse(
    val status: String,
    val assessment: Assessment,

    val screening: ScreeningInterpretation =
        ScreeningInterpretation(),

    @SerializedName("image_result")
    val imageResult: ImageResult? = null,

    @SerializedName("symptom_result")
    val symptomResult: ModelResult = ModelResult(),

    @SerializedName("patient_result")
    val patientResult: ModelResult = ModelResult(),

    val uncertainty: UncertaintyResult =
        UncertaintyResult()
)

data class Assessment(
    @SerializedName("image_type")
    val imageType: String? = null,
    val finding: String? = null,
    val confidence: Double? = null,
    val probabilities: Map<String, Double> = emptyMap()
)

data class ImageResult(
    val type: String? = null,
    val prediction: ImagePrediction? = null
)

data class ImagePrediction(
    @SerializedName("class_index")
    val classIndex: Int? = null,
    @SerializedName("class_name")
    val className: String? = null,
    val confidence: Double? = null,
    val probabilities: Map<String, Double> = emptyMap()
)

data class ModelResult(
    @SerializedName("class_index")
    val classIndex: Int? = null,
    @SerializedName("class_name")
    val className: String? = null,
    val confidence: Double? = null,
    val probabilities: Map<String, Double> = emptyMap()
)

data class UncertaintyResult(
    val confidence: Double = 0.0,
    val uncertainty: Double = 0.0,
    val completeness: Double = 0.0,
    @SerializedName("image_quality")
    val imageQuality: Double? = null
)

data class ScreeningInterpretation(
    @SerializedName("main_concern")
    val mainConcern: String = "",

    @SerializedName("overall_status")
    val overallStatus: String = "",

    @SerializedName("screening_summary")
    val screeningSummary: String = "",

    val triage: String = "",

    @SerializedName("red_flags")
    val redFlags: List<String> = emptyList(),

    @SerializedName("vitals_interpretation")
    val vitalsInterpretation: String = "",

    @SerializedName("model_explanations")
    val modelExplanations: List<String> = emptyList(),

    @SerializedName("next_steps")
    val nextSteps: String = "",

    @SerializedName("overall_explanation")
    val overallExplanation: String = ""
)