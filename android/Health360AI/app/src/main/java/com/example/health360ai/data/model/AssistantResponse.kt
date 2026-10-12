package com.example.health360ai.data.remote.model

import com.google.gson.JsonObject

data class AssistantResponse(
    val status: String,
    val message: String,
    val context: JsonObject? = null
)