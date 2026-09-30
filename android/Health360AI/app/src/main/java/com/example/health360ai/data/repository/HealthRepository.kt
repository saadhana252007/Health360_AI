package com.example.health360ai.data.repository

import com.example.health360ai.data.remote.CheckupRequest
import com.example.health360ai.data.remote.CheckupResponse
import com.example.health360ai.data.remote.RetrofitClient
import com.example.health360ai.data.supabase.supabase
import io.github.jan.supabase.auth.auth

class HealthRepository {

    suspend fun checkHealth(): Map<String, String> {
        return RetrofitClient.api.healthCheck()
    }

    suspend fun analyzeCheckup(
        symptoms: Map<String, Any>,
        patient: Map<String, Any>
    ): CheckupResponse {
        val session = supabase.auth.currentSessionOrNull()
            ?: throw IllegalStateException("Please log in again")

        val userId = session.user?.id
            ?: throw IllegalStateException("User account not available")

        val request = CheckupRequest(
            user_id = userId,
            symptoms = symptoms,
            patient = patient
        )

        return RetrofitClient.api.analyzeCheckup(request)
    }
}