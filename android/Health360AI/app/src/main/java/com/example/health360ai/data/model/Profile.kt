package com.example.health360ai.data.model

import kotlinx.serialization.Serializable

@Serializable
data class Profile(
    val id: String,
    val full_name: String,
    val date_of_birth: String,
    val sex: String,
    val height_cm: Double,
    val weight_kg: Double,
    val created_at: String? = null,
    val updated_at: String? = null
)