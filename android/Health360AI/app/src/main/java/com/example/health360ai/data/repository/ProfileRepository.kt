package com.example.health360ai.data.repository

import com.example.health360ai.data.model.Profile
import com.example.health360ai.data.supabase.supabase
import io.github.jan.supabase.postgrest.from

class ProfileRepository {

    suspend fun getProfile(userId: String): Profile? {
        return supabase
            .from("profiles")
            .select {
                filter {
                    eq("id", userId)
                }
            }
            .decodeSingleOrNull<Profile>()
    }

    suspend fun updateProfile(profile: Profile) {
        supabase
            .from("profiles")
            .update(profile) {
                filter {
                    eq("id", profile.id)
                }
            }
    }
}