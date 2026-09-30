package com.example.health360ai.data.supabase

import com.example.health360ai.BuildConfig
import io.github.jan.supabase.auth.Auth
import io.github.jan.supabase.postgrest.Postgrest
import io.github.jan.supabase.createSupabaseClient
import io.github.jan.supabase.auth.FlowType

val supabase = createSupabaseClient(
    supabaseUrl = BuildConfig.SUPABASE_URL,
    supabaseKey = BuildConfig.SUPABASE_PUBLISHABLE_KEY
) {
    install(Auth) {
        flowType = FlowType.PKCE
        scheme = "health360"
        host = "login"
    }

    install(Postgrest)
}