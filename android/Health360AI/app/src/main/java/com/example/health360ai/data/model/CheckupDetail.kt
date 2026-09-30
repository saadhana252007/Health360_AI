package com.example.health360ai.data.model

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonObject

@Serializable
data class CheckupDetail(
    val id: String,
    val user_id: String,
    val status: String,
    val overall_score: Double,
    val overall_category: String? = null,
    val confidence: Double? = null,
    val uncertainty: Double? = null,
    val completeness: Double? = null,
    val symptoms: JsonObject? = null,
    val patient_data: JsonObject? = null,
    val image_result: JsonObject? = null,
    val symptom_result: JsonObject? = null,
    val patient_result: JsonObject? = null,
    val fusion_result: JsonObject? = null,
    val screening: JsonObject? = null,
    val uncertainty_data: JsonObject? = null,
    val created_at: String
)