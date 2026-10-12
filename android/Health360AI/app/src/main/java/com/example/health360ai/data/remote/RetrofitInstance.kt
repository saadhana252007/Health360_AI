package com.example.health360ai.data.remote

// RetrofitInstance used to be a second copy of RetrofitClient with its own
// hard-coded address. It now points at RetrofitClient so there is a single
// place that sets the base URL and the login token.
object RetrofitInstance {

    val api: Health360ApiService
        get() = RetrofitClient.api
}
