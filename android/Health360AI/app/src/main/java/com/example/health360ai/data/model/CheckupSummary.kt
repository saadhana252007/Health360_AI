package com.example.health360ai.data.model

import kotlinx.serialization.Serializable

@Serializable
data class CheckupSummary(
    val id: String,
    val user_id: String,
    val status: String,
    val overall_score: Double,
    val overall_category: String? = null,
    val confidence: Double? = null,
    val uncertainty: Double? = null,
    val completeness: Double? = null,
    val created_at: String,
    val screening: ScreeningSummary? = null,
    val image_result: ImageHistoryResult? = null,
    val symptom_result: ModelHistoryResult? = null,
    val patient_result: ModelHistoryResult? = null
)

@Serializable
data class ScreeningSummary(
    val main_concern: String? = null,
    val overall_status: String? = null,
    val screening_summary: String? = null,
    val triage: String? = null,
    val red_flags: List<String> = emptyList(),
    val vitals_interpretation: String? = null,
    val next_steps: String? = null
)

@Serializable
data class ImageHistoryResult(
    val type: String? = null,
    val prediction: ImageHistoryPrediction? = null
)

@Serializable
data class ImageHistoryPrediction(
    val class_name: String? = null,
    val confidence: Double? = null
)

@Serializable
data class ModelHistoryResult(
    val class_name: String? = null,
    val confidence: Double? = null
)