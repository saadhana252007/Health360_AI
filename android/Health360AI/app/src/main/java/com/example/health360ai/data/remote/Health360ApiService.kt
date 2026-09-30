package com.example.health360ai.data.remote

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface Health360ApiService {

    @GET("health")
    suspend fun healthCheck(): Map<String, String>

    @POST("api/v1/checkups/analyze")
    suspend fun analyzeCheckup(
        @Body request: CheckupRequest
    ): CheckupResponse

    @Multipart
    @POST("api/v1/checkups/analyze-image")
    suspend fun analyzeCheckupWithImage(
        @Part("user_id") userId: RequestBody,
        @Part("symptoms") symptoms: RequestBody,
        @Part("patient") patient: RequestBody,
        @Part("image_type") imageType: RequestBody,
        @Part image: MultipartBody.Part
    ): CheckupResponse
}