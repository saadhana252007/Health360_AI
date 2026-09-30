package com.example.health360ai.data.model

import kotlinx.serialization.Serializable

@Serializable
data class Symptom(
    val complaint_type: String,
    val severity: Double,
    val duration_days: Double,
    val frequency: Double,
    val progression: Double,
    val site: String,
    val character: Double,
    val trigger: Double,
    val associated_symptoms: List<String>,
    val pre_symptoms: List<String>,
    val post_symptoms: List<String>
)