package com.example.health360ai.data.remote.model

data class AssistantRequest(
    val user_id: String,
    val message: String,
    val checkup_id: String? = null
)