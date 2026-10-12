package com.example.health360ai.data.remote

import com.example.health360ai.BuildConfig
import com.example.health360ai.data.supabase.supabase
import io.github.jan.supabase.auth.auth
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {

    // Set API_BASE_URL in local.properties (see app/build.gradle.kts).
    private val BASE_URL: String =
        BuildConfig.API_BASE_URL.let {
            if (it.endsWith("/")) it else "$it/"
        }

    // Adds the logged-in user's Supabase access token to every request so the
    // backend can work out who the user is.
    private val authInterceptor = Interceptor { chain ->
        val token = supabase.auth.currentSessionOrNull()?.accessToken

        val request = chain.request().newBuilder().apply {
            if (!token.isNullOrBlank()) {
                header("Authorization", "Bearer $token")
            }
        }.build()

        chain.proceed(request)
    }

    // Request and response bodies contain health data, so they are only
    // logged in debug builds, and the token is never printed.
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = if (BuildConfig.DEBUG) {
            HttpLoggingInterceptor.Level.BODY
        } else {
            HttpLoggingInterceptor.Level.NONE
        }
        redactHeader("Authorization")
    }

    private val client = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()

    val api: Health360ApiService = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(client)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(Health360ApiService::class.java)
}
