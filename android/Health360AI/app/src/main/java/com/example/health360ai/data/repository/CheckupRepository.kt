package com.example.health360ai.data.repository

import android.content.Context
import com.example.health360ai.data.model.CheckupDetail
import com.example.health360ai.data.model.CheckupSummary
import com.example.health360ai.data.remote.CheckupRequest
import com.example.health360ai.data.remote.CheckupResponse
import com.example.health360ai.data.remote.RetrofitClient
import com.example.health360ai.data.supabase.supabase
import com.google.gson.Gson
import io.github.jan.supabase.auth.auth
import io.github.jan.supabase.postgrest.from
import io.github.jan.supabase.postgrest.query.Order
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody

class CheckupRepository(
    private val context: Context
) {

    suspend fun submitCheckup(): CheckupResponse {

        val session = supabase.auth.currentSessionOrNull()
            ?: throw IllegalStateException("Please log in again")

        val userId = session.user?.id
            ?: throw IllegalStateException("User account not available")

        val patient = CheckupStateRepository.patient
            ?: throw IllegalStateException("Patient information is missing")

        val symptoms = CheckupStateRepository.symptoms
            ?: throw IllegalStateException("Symptoms are missing")

        val vitals = CheckupStateRepository.vitals

        val patientData = mutableMapOf<String, Any>(
            "full_name" to patient.full_name,
            "date_of_birth" to patient.date_of_birth,
            "sex" to patient.sex,
            "height_cm" to patient.height_cm,
            "weight_kg" to patient.weight_kg
        )

        patientData.putAll(vitals)

        val symptomsData = mapOf(
            "complaint_type" to symptoms.complaint_type,
            "severity" to symptoms.severity,
            "duration_days" to symptoms.duration_days,
            "frequency" to symptoms.frequency,
            "progression" to symptoms.progression,
            "site" to symptoms.site,
            "character" to symptoms.character,
            "trigger" to symptoms.trigger,
            "associated_symptoms" to symptoms.associated_symptoms,
            "pre_symptoms" to symptoms.pre_symptoms,
            "post_symptoms" to symptoms.post_symptoms
        )

        val gson = Gson()

        val patientJson = gson.toJson(patientData)
        val symptomsJson = gson.toJson(symptomsData)

        val imageUri = CheckupStateRepository.imageUri
        val imageType = CheckupStateRepository.imageType

        if (imageUri == null || imageType == null) {
            return RetrofitClient.api.analyzeCheckup(
                CheckupRequest(
                    user_id = userId,
                    symptoms = symptomsData,
                    patient = patientData
                )
            )
        }

        val userIdBody = userId.toRequestBody(
            "text/plain".toMediaType()
        )

        val patientBody = patientJson.toRequestBody(
            "application/json".toMediaType()
        )

        val symptomsBody = symptomsJson.toRequestBody(
            "application/json".toMediaType()
        )

        val imageTypeBody = imageType.toRequestBody(
            "text/plain".toMediaType()
        )

        val imageBytes = context.contentResolver
            .openInputStream(imageUri)
            ?.use { it.readBytes() }
            ?: throw IllegalStateException("Unable to read selected image")

        val imageBody = imageBytes.toRequestBody(
            "image/*".toMediaType()
        )

        val imagePart = MultipartBody.Part.createFormData(
            "image",
            "health360_image.jpg",
            imageBody
        )

        return RetrofitClient.api.analyzeCheckupWithImage(
            userId = userIdBody,
            symptoms = symptomsBody,
            patient = patientBody,
            imageType = imageTypeBody,
            image = imagePart
        )
    }

    suspend fun getLatestCheckup(
        userId: String
    ): CheckupSummary? {
        return supabase
            .from("checkups")
            .select {
                filter {
                    eq("user_id", userId)
                }
                order(
                    column = "created_at",
                    order = Order.DESCENDING
                )
                limit(1)
            }
            .decodeList<CheckupSummary>()
            .firstOrNull()
    }

    suspend fun getCheckupHistory(
        userId: String
    ): List<CheckupSummary> {
        return supabase
            .from("checkups")
            .select {
                filter {
                    eq("user_id", userId)
                }
                order(
                    column = "created_at",
                    order = Order.DESCENDING
                )
            }
            .decodeList<CheckupSummary>()
    }

    suspend fun getCheckupDetail(
        checkupId: String,
        userId: String
    ): CheckupDetail? {
        return supabase
            .from("checkups")
            .select {
                filter {
                    eq("id", checkupId)
                    eq("user_id", userId)
                }
            }
            .decodeList<CheckupDetail>()
            .firstOrNull()
    }
}